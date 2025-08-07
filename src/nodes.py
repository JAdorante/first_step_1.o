from colorama import Fore, Style
from .tools.base.markdown_scraper_tool import scrape_website_to_markdown
from .tools.base.search_tools import get_recent_news, google_search
from .tools.base.gmail_tools import GmailTools
from .tools.google_docs_tools import GoogleDocsManager
from .tools.lead_research import research_lead_on_linkedin
from .tools.company_research import research_lead_company, generate_company_profile
from .tools.youtube_tools import get_youtube_stats
from .tools.rag_tool import fetch_similar_case_study
from .prompts import *
from .state import LeadData, CompanyData, Report, GraphInputState, GraphState
from .structured_outputs import WebsiteData, EmailResponse
from .utils import invoke_llm, get_report, get_current_date, save_reports_locally

# Enable or disable sending emails directly using GMAIL
# Should be confident about the quality of the email
SEND_EMAIL_DIRECTLY = True
# New flag: If True, send an email directly to the decision maker found on LinkedIn if their email is public
SEND_EMAIL_TO_LINKEDIN_PERSON = True
# Enable or disable saving emails to Google Docs
# By defauly all reports are save locally in `reports` folder
SAVE_TO_GOOGLE_DOCS = True

# Add this flag to switch between modes
INDUSTRY_RESEARCH_MODE = True  # Set to True to find new companies by industry
STOP_AFTER_FIRST_QUALIFIED = True  # Stop after first qualified company

# In src/nodes.py or wherever appropriate
INDUSTRIES_TO_RESEARCH = [
    "Healthcare",
    "Retail",
    "Manufacturing",
    "Defense",
    "AI",
    "Industrial automation",
    "Computer Vision",
    "Telco"
]

# Import random at the top of the file
import random
import time
import os
import json
from datetime import datetime

# Set a random seed based on current time for different randomization each run
random.seed(time.time())

class OutReachAutomationNodes:
    def __init__(self, loader, existing_clients_sheet_id=None):
        self.lead_loader = loader
        self.docs_manager = GoogleDocsManager()
        self.drive_folder_name = ""
        
        # Initialize processed companies logging
        self.processed_companies_file = "processed_companies.json"
        self.processed_companies = self._load_processed_companies()
        
        # Load existing clients from Google Sheets if sheet ID provided
        if existing_clients_sheet_id:
            from .tools.existing_clients_loader import ExistingClientsLoader
            clients_loader = ExistingClientsLoader(existing_clients_sheet_id)
            self.existing_clients = clients_loader.get_existing_clients()
        else:
            # Fallback to hardcoded list
            self.existing_clients = ["Genetec", "Nokia", "Siemens", "Google", "Palentir", "Emerson"]
        
        print(f"Excluding {len(self.existing_clients)} existing clients: {', '.join(self.existing_clients[:5])}...")
        print(f"Loaded {len(self.processed_companies)} previously processed companies from log")
        
        # Show recent processed companies if any exist
        if self.processed_companies:
            print("\nRecent processed companies:")
            recent = self.processed_companies[-5:]  # Show last 5
            for company in recent:
                print(f"  • {company['name']} ({company.get('industry', 'N/A')})")
            print()

    def _load_processed_companies(self):
        """Load the list of previously processed companies from JSON file"""
        try:
            if os.path.exists(self.processed_companies_file):
                with open(self.processed_companies_file, 'r') as f:
                    data = json.load(f)
                    return data.get('companies', [])
            else:
                # Create the file if it doesn't exist
                self._save_processed_companies([])
                return []
        except Exception as e:
            print(f"Warning: Could not load processed companies log: {e}")
            return []

    def _save_processed_companies(self, companies_list=None):
        """Save the list of processed companies to JSON file"""
        try:
            if companies_list is None:
                companies_list = self.processed_companies
            
            data = {
                'last_updated': datetime.now().isoformat(),
                'companies': companies_list
            }
            
            with open(self.processed_companies_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save processed companies log: {e}")

    def _add_processed_company(self, company_name, industry=None, linkedin_url=None):
        """Add a company to the processed companies log"""
        company_info = {
            'name': company_name,
            'industry': industry,
            'linkedin_url': linkedin_url,
            'processed_date': datetime.now().isoformat()
        }
        
        # Check if company already exists (case-insensitive)
        normalized_name = company_name.lower().strip()
        existing_names = [c['name'].lower().strip() for c in self.processed_companies]
        
        if normalized_name not in existing_names:
            self.processed_companies.append(company_info)
            self._save_processed_companies()
            print(f"Added {company_name} to processed companies log")
        else:
            print(f"Company {company_name} already in processed log")

    def _is_company_processed(self, company_name):
        """Check if a company has already been processed"""
        normalized_name = company_name.lower().strip()
        existing_names = [c['name'].lower().strip() for c in self.processed_companies]
        return normalized_name in existing_names

    def get_processed_companies_summary(self):
        """Get a summary of processed companies"""
        if not self.processed_companies:
            return "No companies have been processed yet."
        
        summary = f"Total processed companies: {len(self.processed_companies)}\n"
        summary += "Recent companies:\n"
        
        # Show last 10 companies
        recent_companies = self.processed_companies[-10:]
        for company in recent_companies:
            summary += f"- {company['name']} ({company.get('industry', 'N/A')}) - {company['processed_date'][:10]}\n"
        
        return summary

    def clear_processed_companies_log(self):
        """Clear the processed companies log (use with caution)"""
        self.processed_companies = []
        self._save_processed_companies()
        print("Processed companies log cleared")

    def export_processed_companies(self, filename="processed_companies_export.json"):
        """Export processed companies to a separate file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.processed_companies, f, indent=2)
            print(f"Processed companies exported to {filename}")
        except Exception as e:
            print(f"Error exporting processed companies: {e}")

    def get_linkedin_links_for_company(self, company_name):
        """Get LinkedIn links for a specific company from the processed log"""
        normalized_search = company_name.lower().strip()
        
        for company in self.processed_companies:
            if normalized_search in company['name'].lower():
                links = []
                if company.get('linkedin_url'):
                    links.append(f"Company: {company['linkedin_url']}")
                if company.get('decision_maker_linkedin'):
                    links.append(f"Decision Maker: {company['decision_maker_linkedin']}")
                
                if links:
                    return f"LinkedIn links for {company['name']}:\n" + "\n".join(links)
                else:
                    return f"No LinkedIn links found for {company['name']}"
        
        return f"Company '{company_name}' not found in processed log"

    def get_new_leads(self, state: GraphInputState):
        if INDUSTRY_RESEARCH_MODE:
            return self._get_industry_research_leads(state)
        else:
            return self._get_standard_leads(state)
    
    def _get_standard_leads(self, state: GraphInputState):
        """Original lead fetching logic"""
        print(Fore.YELLOW + "----- Fetching new leads -----\n" + Style.RESET_ALL)
        
        # Fetch new leads using the provided loader
        raw_leads = self.lead_loader.fetch_records()
        
        # Structure the leads
        leads = [
            LeadData(
                id=lead["id"],
                name=f'{lead.get("First Name", "")} {lead.get("Last Name", "")}',
                email=lead.get("Email", ""),
                phone=lead.get("Phone", ""),
                address=lead.get("Address", ""),
                profile="" # will be constructed
            )
            for lead in raw_leads
        ]
        
        print(Fore.YELLOW + f"----- Fetched {len(leads)} leads -----\n" + Style.RESET_ALL)
        return {"leads_data": leads, "number_leads": len(leads)}
    
    def _get_industry_research_leads(self, state: GraphInputState):
        """Create virtual leads for industry research"""
        print(Fore.YELLOW + "----- Fetching industries from existing clients -----\n" + Style.RESET_ALL)
        
        # Fetch all records to extract industries
        raw_records = self.lead_loader.fetch_records()
        
        # Extract unique industries from the records
        industries = set()
        for record in raw_records:
            # Try different possible field names - including Column 16 which appears to be Industry
            industry = (record.get("Industry") or 
                       record.get("industry") or 
                       record.get("INDUSTRY") or 
                       record.get("Column 16") or  # This is where industry data is in your current table
                       "")
            if industry and industry not in ["", "None", None]:
                industries.add(industry)
        
        print(f"Found industries: {industries}")
        
        # Create a copy of the industries list and shuffle it randomly
        shuffled_industries = INDUSTRIES_TO_RESEARCH.copy()
        random.shuffle(shuffled_industries)
        print(f"Randomized industry order: {shuffled_industries}")
        
        # Create "virtual leads" for industry research
        leads = []
        for industry in shuffled_industries:
            # Check if this industry has been exhausted
            if self._is_company_processed(f"INDUSTRY_EXHAUSTED_{industry}"):
                print(f"Skipping exhausted industry: {industry}")
                continue
                
            # Create a placeholder lead for each industry
            leads.append(LeadData(
                id=f"industry_{industry.replace(' ', '_')}",
                name=f"New {industry} Company Research",
                email="jadorant@villanova.edu",  # Use your real email here
                phone="",
                address="",
                profile=industry  # Store industry in profile field
            ))
        
        print(Fore.YELLOW + f"----- Created {len(leads)} industry research tasks -----\n" + Style.RESET_ALL)
        return {"leads_data": leads, "number_leads": len(leads)}
    
    @staticmethod
    def check_for_remaining_leads(state: GraphState):
        """Checks for remaining leads and updates lead_data in the state."""
        print(Fore.YELLOW + "----- Checking for remaining leads -----\n" + Style.RESET_ALL)
        
        current_lead = None
        if state["leads_data"]:
            current_lead = state["leads_data"].pop()
        return {"current_lead": current_lead}

    @staticmethod
    def check_if_there_more_leads(state: GraphState):
        # Number of leads remaining
        num_leads = state["number_leads"]
        if num_leads > 0:
            print(Fore.YELLOW + f"----- Found {num_leads} more leads -----\n" + Style.RESET_ALL)
            return "Found leads"
        else:
            print(Fore.GREEN + "----- Finished, No more leads -----\n" + Style.RESET_ALL)
            return "No more leads"

    def fetch_linkedin_profile_data(self, state: GraphState):
        if INDUSTRY_RESEARCH_MODE and state["current_lead"].id.startswith("industry_"):
            return self._fetch_industry_company_data(state)
        else:
            return self._fetch_standard_linkedin_data(state)
    
    def _fetch_standard_linkedin_data(self, state: GraphState):
        """Original LinkedIn fetching logic"""
        print(Fore.YELLOW + "----- Searching Lead data on LinkedIn -----\n" + Style.RESET_ALL)
        lead_data = state["current_lead"]
        company_data = state.get("company_data", CompanyData())
        
        # Scrape lead linkedin profile
        result = research_lead_on_linkedin(lead_data.name, lead_data.email)
        if isinstance(result, str):
            # Handle error message (e.g., skip, log, or set defaults)
            lead_profile = company_name = company_website = company_linkedin_url = ""
        else:
            lead_profile, company_name, company_website, company_linkedin_url = result
       
        lead_data.profile = str(lead_profile) if lead_profile is not None else ""

        # Research company on linkedin
        company_profile = research_lead_company(company_linkedin_url)
        
        # Update company name from LinkedIn data, ensuring non-None values
        company_data.name = str(company_name) if company_name is not None else ""
        company_data.website = str(company_website) if company_website is not None else ""
        company_data.profile = str(company_profile) if company_profile is not None else ""
            
        # Update folder name for saving reports in Drive
        self.drive_folder_name = f"{lead_data.name}_{company_data.name}"
        
        return {
            "current_lead": lead_data,
            "company_data": company_data,
            "reports": []
        }
    
    def _fetch_industry_company_data(self, state: GraphState):
        """New industry-based company discovery"""
        print(Fore.YELLOW + "----- Searching for new companies in industry -----\n" + Style.RESET_ALL)
        lead_data = state["current_lead"]
        industry = lead_data.profile  # We stored industry here
        company_data = state.get("company_data", CompanyData())
        
        # Search for companies in this industry, excluding existing clients
        # Limit exclusion to top 30 clients to avoid overly long queries
        exclude_terms = " ".join([f'-"{client}"' for client in self.existing_clients[:10]])
        search_query = f'"{industry}" companies {exclude_terms} site:linkedin.com/company/'
        print(f"Searching: {search_query}")
        
        search_results = google_search(search_query)
        print(f"Google search query: {search_query}")
        print(f"Number of search results: {len(search_results)}")
        for i, result in enumerate(search_results[:5]):
            print(f"Result {i}: {result}")
        
        # More robust company name comparison
        def normalize(name):
            return name.lower().replace("inc.", "").replace("ltd.", "").replace("corp.", "").strip()

        target_company = None
        for result in search_results[:30]:
            link = result.get('link', '')
            title = result.get('title', '')
            company_name = title.split(' | ')[0].strip()
            if '/company/' in link:
                # Check against existing clients
                if any(normalize(client) == normalize(company_name) for client in self.existing_clients):
                    print(f"Skipping existing client: {company_name}")
                    continue
                
                # Check against previously processed companies
                if self._is_company_processed(company_name):
                    print(f"Skipping previously processed company: {company_name}")
                    continue
                
                # Found a new company!
                target_company = {
                    'name': company_name,
                    'linkedin_url': link,
                    'snippet': result.get('snippet', '')
                }
                print(f"Found new unprocessed company: {company_name}")
                break
        
        if target_company:
            print(f"Found new company: {target_company['name']}")
            
            # Add company to processed log immediately to avoid reprocessing
            self._add_processed_company(
                company_name=target_company['name'],
                industry=industry,
                linkedin_url=target_company['linkedin_url']
            )
            
            # Research the company
            company_profile = research_lead_company(target_company['linkedin_url'])
            
            # Now find decision makers at this company
            dm_query = f'site:linkedin.com/in/ "{target_company["name"]}" ("CEO" OR "CTO" OR "CMO" OR "VP Marketing" OR "Head of Marketing")'
            dm_results = google_search(dm_query)
            
            # Extract first decision maker
            if dm_results:
                # Use the simpler extraction method instead of invoking LLM
                dm_linkedin_url = ""
                for result in dm_results:
                    if 'linkedin.com/in/' in result.get('link', ''):
                        dm_linkedin_url = result['link']
                        break
                
                if dm_linkedin_url:
                    # Scrape decision maker profile
                    from .tools.base.linkedin_tools import scrape_linkedin
                    dm_data = scrape_linkedin(dm_linkedin_url)
                    
                    if dm_data and "data" in dm_data:
                        profile_data = dm_data["data"]
                        lead_data.name = profile_data.get('full_name', 'Decision Maker')
                        # Try to get public email from LinkedIn profile
                        public_email = profile_data.get('email')
                        if public_email and isinstance(public_email, str) and '@' in public_email:
                            lead_data.email = public_email
                            print(f"Found public email for decision maker: {public_email}")
                            # Send email if feature is enabled
                            if SEND_EMAIL_TO_LINKEDIN_PERSON:
                                from .tools.base.gmail_tools import GmailTools
                                gmail = GmailTools()
                                # Generate a simple subject and message, or use your existing email generation logic
                                subject = f"Hello {lead_data.name}"
                                email_content = f"Hi {lead_data.name},\n\nI came across your profile and wanted to connect regarding potential collaboration.\n\nBest regards,\n[Your Name]"
                                gmail.create_draft_email(
                                    recipient=public_email,
                                    subject=subject,
                                    email_content=email_content
                                )
                                if SEND_EMAIL_DIRECTLY:
                                    gmail.send_email(
                                        recipient=public_email,
                                        subject=subject,
                                        email_content=email_content
                                    )
                                    print(f"Email sent directly to {public_email}")
                        else:
                            # Fallback to default email if no public email found
                            company_name_clean = target_company['name'].lower().replace(' ', '').replace(',', '').replace('.', '').replace('&', 'and')
                            lead_data.email = "jadorant@villanova.edu"  # Change this to your actual email
                        lead_data.profile = f"{profile_data.get('headline', '')}. {profile_data.get('about', '')}"
                    # Store decision maker LinkedIn URL
                    company_data.decision_maker_linkedin = dm_linkedin_url
            
            # Update company data
            company_data.name = target_company['name']
            company_data.profile = str(company_profile) if company_profile else target_company['snippet']
            company_data.linkedin_url = target_company['linkedin_url']
            
            # Try to find company website
            website_query = f'"{target_company["name"]}" official website'
            website_results = google_search(website_query)
            if website_results:
                # Look for non-LinkedIn, non-social media links
                for result in website_results:
                    link = result.get('link', '')
                    if not any(social in link for social in ['linkedin.com', 'facebook.com', 'twitter.com', 'instagram.com']):
                        company_data.website = link
                        break
        else:
            print(f"No new companies found in {industry} industry")
            # Add a marker to avoid repeatedly searching this industry
            self._add_processed_company(
                company_name=f"INDUSTRY_EXHAUSTED_{industry}",
                industry=industry,
                linkedin_url=None
            )
            # Create placeholder data
            lead_data.name = f"Research Lead - {industry}"
            company_data.name = f"New {industry} Company"
            company_data.profile = f"Potential company in the {industry} industry"
        
        # Update folder name for saving reports in Drive
        self.drive_folder_name = f"{industry}_{company_data.name}"
        
        return {
            "current_lead": lead_data,
            "company_data": company_data,
            "reports": []
        }
    
    def review_company_website(self, state: GraphState):
        print(Fore.YELLOW + "----- Scraping company website -----\n" + Style.RESET_ALL)
        lead_data = state.get("current_lead")
        company_data = state.get("company_data")
        
        company_website = company_data.website
        if company_website:
            try:
                # Scrape company website with improved error handling
                content = scrape_website_to_markdown(company_website, max_length=30000)
                print(f"Scraped content length: {len(content)} characters")
                
                try:
                    website_info = invoke_llm(
                        system_prompt=WEBSITE_ANALYSIS_PROMPT.format(main_url=company_website), 
                        user_message=content,
                        model="gpt-3.5-turbo",
                        llm_provider="openai",
                        response_format=WebsiteData,
                        max_tokens=10000  # Reduced token limit
                    )
                except Exception as e:
                    print(f"Structured output failed, using text response: {e}")
                    # Fallback to text response without structured output
                    try:
                        website_info_text = invoke_llm(
                            system_prompt=WEBSITE_ANALYSIS_PROMPT.format(main_url=company_website), 
                            user_message=content,
                            model="gpt-3.5-turbo",
                            llm_provider="openai",
                            max_tokens=8000  # Further reduced for fallback
                        )
                    except Exception as fallback_error:
                        print(f"Fallback also failed: {fallback_error}")
                        # Create minimal website info
                        website_info_text = f"Unable to analyze website content for {company_website}. Error: {fallback_error}"
                    
                    # Create a mock WebsiteData from text response
                    website_info = {
                        "summary": website_info_text[:500] if isinstance(website_info_text, str) else "",
                        "blog_url": "",
                        "facebook": "",
                        "twitter": "",
                        "youtube": ""
                    }
            except Exception as scraping_error:
                print(f"Website scraping failed: {scraping_error}")
                website_info = {
                    "summary": f"Unable to scrape website {company_website}. Error: {scraping_error}",
                    "blog_url": "",
                    "facebook": "",
                    "twitter": "",
                    "youtube": ""
                }
            # Extract all relevant links, ensuring they are strings (not None)
            def safe_str(val):
                return str(val) if val is not None else ""
            if isinstance(website_info, dict):
                company_data.social_media_links.blog = safe_str(website_info.get("blog_url"))
                company_data.social_media_links.facebook = safe_str(website_info.get("facebook"))
                company_data.social_media_links.twitter = safe_str(website_info.get("twitter"))
                company_data.social_media_links.youtube = safe_str(website_info.get("youtube"))
            else:
                company_data.social_media_links.blog = safe_str(getattr(website_info, "blog_url", None))
                company_data.social_media_links.facebook = safe_str(getattr(website_info, "facebook", None))
                company_data.social_media_links.twitter = safe_str(getattr(website_info, "twitter", None))
                company_data.social_media_links.youtube = safe_str(getattr(website_info, "youtube", None))
            # Update company profile with website summary
            # Safely extract summary from website_info, handling dict, BaseModel, or str
            summary = ""
            if isinstance(website_info, dict):
                summary = website_info.get("summary", "")
            elif hasattr(website_info, "summary"):
                summary = getattr(website_info, "summary", "")
            elif isinstance(website_info, str):
                summary = website_info
            company_data.profile = str(generate_company_profile(company_data.profile, summary))
                 
        inputs = f"""
        # **Lead Profile:**

        {lead_data.profile}

        # **Company Information:**

        {company_data.profile}
        """
        
        # Add industry context if in industry research mode
        if INDUSTRY_RESEARCH_MODE and hasattr(lead_data, 'profile') and lead_data.id.startswith("industry_"):
            industry = lead_data.profile
            inputs += f"""
        
        # **Industry Context:**
        
        This is a new potential client in the {industry} industry. 
        Our existing clients in this industry include: {', '.join([c for c in self.existing_clients if c in ["Genetec", "Siemens", "Nokia", "Google", "Palentir", "Emerson"]])}
        Focus on how this company differs from our existing clients and unique opportunities.
        """
        
        # Generate general lead search report
        general_lead_search_report = invoke_llm(
            system_prompt=LEAD_SEARCH_REPORT_PROMPT, 
            user_message=inputs,
            model="gpt-3.5-turbo",
            llm_provider="openai"
        )
        
        lead_search_report = Report(
            title="General Lead Research Report",
            content=str(general_lead_search_report),
            is_markdown=True
        )
        
        return {
            "company_data": company_data,
            "reports": [lead_search_report]
        }
    
    @staticmethod
    def collect_company_information(state: GraphState):
        return {"reports": []}
    
    def analyze_blog_content(self, state: GraphState):
        print(Fore.YELLOW + "----- Analyzing company main blog -----\n" + Style.RESET_ALL)  
        blog_analysis_report = ""
        
        # Check if company has a blog
        company_data = state["company_data"]
        blog_url = company_data.social_media_links.blog
        if blog_url:
            try:
                blog_content = scrape_website_to_markdown(blog_url, max_length=25000)
                print(f"Blog content length: {len(blog_content)} characters")
                
                from .prompts import BLOG_ANALYSIS_PROMPT  # Fix: import the missing prompt
                prompt = BLOG_ANALYSIS_PROMPT.format(company_name=company_data.name)
                
                try:
                    blog_analysis_report = invoke_llm(
                        system_prompt=prompt, 
                        user_message=blog_content,
                        model="gpt-3.5-turbo",
                        llm_provider="openai",
                        max_tokens=8000
                    )
                except Exception as e:
                    print(f"Blog analysis failed: {e}")
                    blog_analysis_report = f"Unable to analyze blog content for {company_data.name}. Error: {e}"
                
                blog_analysis_report = Report(
                    title="Blog Analysis Report",
                    content=str(blog_analysis_report),
                    is_markdown=True
                )
                
                return {"reports": [blog_analysis_report]}
            except Exception as scraping_error:
                print(f"Blog scraping failed: {scraping_error}")
                blog_analysis_report = Report(
                    title="Blog Analysis Report",
                    content=f"Unable to scrape blog content for {company_data.name}. Error: {scraping_error}",
                    is_markdown=True
                )
                return {"reports": [blog_analysis_report]}
    def analyze_social_media_content(self, state: GraphState):
        print(Fore.YELLOW + "----- Analyzing company social media accounts -----\n" + Style.RESET_ALL)
        
        # Load states
        company_data = state["company_data"]
        
        # Get social media urls
        facebook_url = company_data.social_media_links.facebook
        twitter_url = company_data.social_media_links.twitter
        youtube_url = company_data.social_media_links.youtube
        
        # Check If company has Youtube channel
        youtube_analysis_report = None
        if youtube_url:
            youtube_data = get_youtube_stats(youtube_url)
            prompt = YOUTUBE_ANALYSIS_PROMPT.format(company_name=company_data.name)
            youtube_insight = invoke_llm(
                system_prompt=prompt, 
                user_message=youtube_data,
                model="gpt-3.5-turbo",
                llm_provider="openai"
            )
            youtube_analysis_report = Report(
                title="Youtube Analysis Report",
                content=str(youtube_insight),
                is_markdown=True
            )
        if facebook_url:
            # TODO Add Facebook analysis part
            pass
        
        # Check If company has Twitter account
        if twitter_url:
            # TODO Add Twitter analysis part
            pass
        
        reports = []
        if youtube_analysis_report is not None:
            reports.append(youtube_analysis_report)

        return {
            "company_data": company_data,
            "reports": reports
        }
    
    def analyze_recent_news(self, state: GraphState):
        print(Fore.YELLOW + "----- Analyzing recent news about company -----\n" + Style.RESET_ALL)
        
        # Load states
        company_data = state["company_data"]
        
        # Fetch recent news using serper API
        recent_news = get_recent_news(company=company_data.name)
        number_months = 6
        current_date = get_current_date()
        news_analysis_prompt = NEWS_ANALYSIS_PROMPT.format(
            company_name=company_data.name, 
            number_months=number_months, 
            date=current_date
        )
        
        # Craft news analysis prompt
        news_insight = invoke_llm(
            system_prompt=news_analysis_prompt, 
            user_message=recent_news,
            model="gpt-3.5-turbo",
            llm_provider="openai"
        )
        
        news_analysis_report = Report(
            title="News Analysis Report",
            content=str(news_insight),
            is_markdown=True
        )
        return {"reports": [news_analysis_report]}
    def generate_digital_presence_report(self, state: GraphState):
        print(Fore.YELLOW + "----- Generate Digital presence analysis report -----\n" + Style.RESET_ALL)
        
        # Load reports
        reports = state["reports"]
        blog_analysis_report = get_report(reports, "Blog Analysis Report")
        facebook_analysis_report = get_report(reports, "Facebook Analysis Report")
        twitter_analysis_report = get_report(reports, "Twitter Analysis Report")
        youtube_analysis_report = get_report(reports, "Youtube Analysis Report")
        news_analysis_report = get_report(reports, "News Analysis Report")
        
        inputs = f"""
        # **Digital Presence Data:**
        ## **Blog Information:**

        {blog_analysis_report}
        
        ## **Facebook Information:**

        {facebook_analysis_report}
        
        ## **Twitter Information:**

        {twitter_analysis_report}

        ## **Youtube Information:**

        {youtube_analysis_report}

        # **Recent News:**

        {news_analysis_report}
        """
        
        prompt = DIGITAL_PRESENCE_REPORT_PROMPT.format(
            company_name=state["company_data"].name, date=get_current_date()
        )
        digital_presence_report = invoke_llm(
            system_prompt=prompt, 
            user_message=inputs,
            model="gpt-3.5-turbo",
            llm_provider="openai"
        ) 
        
        digital_presence_report = Report(
            title="Digital Presence Report",
            content=str(digital_presence_report),
            is_markdown=True
        )
        return {"reports": [digital_presence_report]}
    def generate_full_lead_research_report(self, state: GraphState):
        print(Fore.YELLOW + "----- Generate global lead analysis report -----\n" + Style.RESET_ALL)
        
        # Load reports
        reports = state["reports"]
        general_lead_search_report = get_report(reports, "General Lead Research Report")
        digital_presence_report = get_report(reports, "Digital Presence Report")
        
        inputs = f"""
        # **Lead & company Information:**

        {general_lead_search_report}
        
        ---

        # **Digital Presence Information:**

        {digital_presence_report}
        """
        
        prompt = GLOBAL_LEAD_RESEARCH_REPORT_PROMPT.format(
            company_name=state["company_data"].name, date=get_current_date()
        )
        full_report = invoke_llm(
            system_prompt=prompt, 
            user_message=inputs,
            model="gpt-3.5-turbo",
            llm_provider="openai"
        )
        
        global_research_report = Report(
            title="Global Lead Analysis Report",
            content=str(full_report),
            is_markdown=True
        )
        return {"reports": [global_research_report]}
    @staticmethod
    def score_lead(state: GraphState):
        """
        Score the lead based on the company profile and open positions.

        @param state: The current state of the application.
        @return: Updated state with the lead score.
        """
        print(Fore.YELLOW + "----- Scoring lead -----\n" + Style.RESET_ALL)
        
        # Load reports
        reports = state["reports"]
        global_research_report = get_report(reports, "Global Lead Analysis Report")
        
        # Debug: Print what we're scoring
        company_data = state.get("company_data", {})
        if hasattr(company_data, 'name'):
            company_name = company_data.name
        else:
            company_name = 'Unknown Company'
        print(f"Scoring company: {company_name}")
        
        # Scoring lead
        lead_score = invoke_llm(
            system_prompt=SCORE_LEAD_PROMPT,
            user_message=global_research_report,
            model="gpt-3.5-turbo",
            llm_provider="openai"
        )
        
        # Debug: Print raw score response
        print(f"Raw score response: {lead_score}")
        
        # Ensure lead_score is a string before stripping, handle dict or BaseModel if needed
        if isinstance(lead_score, str):
            score = lead_score.strip()
        elif isinstance(lead_score, dict) and "score" in lead_score:
            score = str(lead_score["score"]).strip()
        else:
            score = str(lead_score).strip()
        
        # Debug: Print final score
        print(f"Final score: {score}")
        
        return {"lead_score": score}

    @staticmethod
    def is_lead_qualified(state: GraphState):
        """
        Check if the lead is qualified based on the lead score.

        @param state: The current state of the application.
        @return: Updated state with the qualification status.
        """
        print(Fore.YELLOW + "----- Checking if lead is qualified -----\n" + Style.RESET_ALL)
        return {"reports": []}

    @staticmethod
    def check_if_qualified(state: GraphState):
        """
        Check if the lead is qualified based on the lead score.

        @param state: The current state of the application.
        @return: Updated state with the qualification status.
        """
        # Checking if the lead score is 5 or higher (more reasonable threshold)
        print(f"DEBUG: In check_if_qualified function")
        print(f"DEBUG: Score: {state['lead_score']}")
        is_qualified = float(state["lead_score"]) >= 5
        if is_qualified:
            print(Fore.GREEN + "Lead is qualified\n" + Style.RESET_ALL)
            print(f"DEBUG: Returning 'qualified' - should proceed to email generation")
            
            # Stop after first qualified company to avoid recursion limit
            if STOP_AFTER_FIRST_QUALIFIED:
                print(f"DEBUG: STOP_AFTER_FIRST_QUALIFIED is True, setting number_leads to 0")
                state["number_leads"] = 0
            
            return "qualified"
        else:
            print(Fore.RED + "Lead is not qualified\n" + Style.RESET_ALL)
            print(f"DEBUG: Returning 'not qualified' - will skip email generation")
            return "not qualified"
    
    @staticmethod
    def create_outreach_materials(state: GraphState):
        print(f"DEBUG: In create_outreach_materials function")
        return {"reports": []}
    
    def generate_custom_outreach_report(self, state: GraphState):
        print(Fore.YELLOW + "----- Crafting Custom outreach report based on gathered information -----\n" + Style.RESET_ALL)
        print(f"DEBUG: In generate_custom_outreach_report function")
        
        # Load reports
        reports = state["reports"]
        general_lead_search_report = get_report(reports, "General Lead Research Report")
        global_research_report = get_report(reports, "Global Lead Analysis Report")
        print(f"DEBUG: Loaded reports successfully")
        
        # Get LinkedIn links from company data
        company_data = state.get("company_data", {})
        linkedin_links = ""
        
        # Add company LinkedIn if available
        if hasattr(company_data, 'linkedin_url') and company_data.linkedin_url:
            linkedin_links += f"**🏢 Company LinkedIn:** {company_data.linkedin_url}\n\n"
        
        # Add decision maker LinkedIn if available
        if hasattr(company_data, 'decision_maker_linkedin') and company_data.decision_maker_linkedin:
            linkedin_links += f"**👤 Decision Maker LinkedIn:** {company_data.decision_maker_linkedin}\n\n"
        
        # Add lead's LinkedIn if available (for standard leads)
        current_lead = state.get("current_lead")
        if hasattr(current_lead, 'profile') and current_lead.profile and not current_lead.id.startswith("industry_"):
            # Try to extract LinkedIn URL from lead profile if available
            if "linkedin.com/in/" in current_lead.profile:
                # Extract LinkedIn URL from profile text
                import re
                linkedin_match = re.search(r'https://linkedin\.com/in/[^\s]+', current_lead.profile)
                if linkedin_match:
                    linkedin_links += f"**🎯 Lead LinkedIn:** {linkedin_match.group()}\n\n"
        
        # TODO Create better description to fetch accurate similar case study using RAG
        # get relevant case study
        print(f"DEBUG: About to fetch case study...")
        case_study_report = fetch_similar_case_study(general_lead_search_report)
        print(f"DEBUG: Fetched case study successfully")
        
        inputs = f"""
        **Research Report:**

        {global_research_report}

        ---

        **LinkedIn Links:**

        {linkedin_links}

        ---

        **Case Study:**

        {case_study_report}
        """
        
        # Generate report
        print(f"DEBUG: About to generate outreach report with LLM...")
        custom_outreach_report = invoke_llm(
            system_prompt=GENERATE_OUTREACH_REPORT_PROMPT,
            user_message=inputs,
            model="gpt-3.5-turbo",
            llm_provider="openai"
        )
        print(f"DEBUG: Generated outreach report with LLM successfully")
        
        # Ensure LinkedIn links are properly included in the final report
        print(f"DEBUG: About to proof-read report with LLM...")
        
        # Create a more structured approach to include LinkedIn links
        linkedin_section = ""
        if linkedin_links.strip():
            linkedin_section = f"""

---

## **🔗 Key Contact Information**

*Use these LinkedIn profiles for direct outreach and relationship building:*

{linkedin_links}

---
"""
        
        # Combine the generated report with LinkedIn links
        # Ensure custom_outreach_report is a string
        report_content = str(custom_outreach_report) if custom_outreach_report else ""
        revised_outreach_report = report_content + linkedin_section
        
        print(f"DEBUG: Proof-read report successfully")
        
        # Store report into google docs and get shareable link
        print(f"DEBUG: About to save report to Google Docs...")
        try:
            new_doc = self.docs_manager.add_document(
                content=revised_outreach_report,
                doc_title="Outreach Report",
                folder_name=self.drive_folder_name,
                make_shareable=True,
                folder_shareable=True, # Set to false if only personal or true if with a team
                markdown=True
            )  
            print(f"DEBUG: Saved report to Google Docs successfully")
            
            if new_doc is None or "shareable_url" not in new_doc or "folder_url" not in new_doc:
                print(f"DEBUG: Google Docs returned invalid response, using fallback URLs")
                new_doc = {
                    "shareable_url": "https://elevateAI.com/outreach-report",
                    "folder_url": "https://elevateAI.com/reports"
                }
        except Exception as e:
            print(f"DEBUG: Google Docs save failed: {e}")
            print(f"DEBUG: Using fallback URLs to continue workflow")
            # Clean up temp file if it exists
            try:
                if os.path.exists('temp_markdown.md'):
                    os.remove('temp_markdown.md')
                    print(f"DEBUG: Cleaned up temp_markdown.md")
            except Exception as cleanup_error:
                print(f"DEBUG: Could not clean up temp file: {cleanup_error}")
            new_doc = {
                "shareable_url": "https://elevateAI.com/outreach-report",
                "folder_url": "https://elevateAI.com/reports"
            }
        
        print(f"DEBUG: Generated outreach report successfully")
        return {
            "custom_outreach_report_link": new_doc["shareable_url"],
            "reports_folder_link": new_doc["folder_url"]
        }

    def generate_personalized_email(self, state: GraphState):
        """
        Generate a personalized email for the lead.

        @param state: The current state of the application.
        @return: Updated state with the generated email.
        """
        print(Fore.YELLOW + "----- Generating personalized email -----\n" + Style.RESET_ALL)
        
        # Debug: Print current lead info
        current_lead = state.get("current_lead")
        print(f"DEBUG: Current lead: {current_lead}")
        print(f"DEBUG: Lead email: {getattr(current_lead, 'email', 'No email') if hasattr(current_lead, 'email') else 'No email attribute'}")
        
        # Load reports
        reports = state["reports"]
        general_lead_search_report = get_report(reports, "General Lead Research Report")
        
        lead_data = f"""
        # **Lead & company Information:**

        {general_lead_search_report}

        # Outreach report Link:

        {state["custom_outreach_report_link"]}
        """
        
        print(f"DEBUG: About to generate email with LLM...")
        output = invoke_llm(
            system_prompt=PERSONALIZE_EMAIL_PROMPT,
            user_message=lead_data,
            model="gpt-3.5-turbo",
            llm_provider="openai",
            response_format=EmailResponse
        )
        
        print(f"DEBUG: LLM output: {output}")
        
        # Get relevant fields
        subject = output.get("subject") if isinstance(output, dict) else getattr(output, "subject", None)
        personalized_email = output.get("email") if isinstance(output, dict) else getattr(output, "email", None)
        
        print(f"DEBUG: Subject: {subject}")
        print(f"DEBUG: Email content length: {len(personalized_email) if personalized_email else 0}")
        
        # Get lead email
        email = getattr(current_lead, "email", None) if hasattr(current_lead, "email") else None
        
        print(f"DEBUG: Recipient email: {email}")
        print(f"DEBUG: SEND_EMAIL_DIRECTLY flag: {SEND_EMAIL_DIRECTLY}")
        
        # Validate email address
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid_email = email and re.match(email_pattern, email)
        
        if not is_valid_email:
            print(f"DEBUG: Invalid email address '{email}', skipping email send")
            # Save email with reports for reference anyway
            personalized_email_doc = Report(
                title="Personalized Email",
                content=personalized_email if personalized_email is not None else "",
                is_markdown=False
            )
            return {"reports": [personalized_email_doc]}
        
        # Create draft email
        gmail = GmailTools()
        print(f"DEBUG: Creating draft email...")
        gmail.create_draft_email(
            recipient=email,
            subject=subject,
            email_content=personalized_email
        )
        
        # Send email directly
        if SEND_EMAIL_DIRECTLY:
            print(f"DEBUG: Sending email directly...")
            gmail.send_email(
                recipient=email,
                subject=subject,
                email_content=personalized_email
            )
            print(f"DEBUG: Email sent successfully!")
        else:
            print(f"DEBUG: SEND_EMAIL_DIRECTLY is False, skipping email send")
        
        # Save email with reports for reference
        # Ensure content is a string, fallback to empty string if None
        personalized_email_doc = Report(
            title="Personalized Email",
            content=personalized_email if personalized_email is not None else "",
            is_markdown=False
        )
        return {"reports": [personalized_email_doc]}

    def generate_interview_script(self, state: GraphState):
        print(Fore.YELLOW + "----- Generating interview script -----\n" + Style.RESET_ALL)
        
        # Load reports
        reports = state["reports"]
        global_research_report = get_report(reports, "Global Lead Analysis Report")
        
        # Generating SPIN questions
        spin_questions = invoke_llm(
            system_prompt=GENERATE_SPIN_QUESTIONS_PROMPT,
            user_message=global_research_report,
            model="gpt-3.5-turbo",
            llm_provider="openai"
        )
        
        inputs = f"""
        # **Lead & company Information:**

        {global_research_report}

        # **SPIN questions:**

        {spin_questions}
        """
        
        # Generating interview script
        interview_script = invoke_llm(
            system_prompt=WRITE_INTERVIEW_SCRIPT_PROMPT,
            user_message=inputs,
            model="gpt-3.5-turbo",
            llm_provider="openai"
        )
        
        # Ensure content is a string, fallback to empty string if None
        interview_script_doc = Report(
            title="Interview Script",
            content=interview_script if isinstance(interview_script, str) else "",
            is_markdown=True
        )
        
        return {"reports": [interview_script_doc]}
    
    @staticmethod
    def await_reports_creation(state: GraphState):
        return {"reports": []}
    
    def save_reports_to_google_docs(self, state: GraphState):
        print(Fore.YELLOW + "----- Save Reports to Google Docs -----\n" + Style.RESET_ALL)
        
        # Load all reports
        reports = state["reports"]
        
        # Ensure reports are saved locally
        save_reports_locally(reports)
        
        # Save all reports to Google docs
        if SAVE_TO_GOOGLE_DOCS:
            for report in reports:
                self.docs_manager.add_document(
                    content=report.content,
                    doc_title=report.title,
                    folder_name=self.drive_folder_name,
                    markdown=report.is_markdown
                )

        return state

    def update_CRM(self, state: GraphState):
        print(Fore.YELLOW + "----- Updating CRM records -----\n" + Style.RESET_ALL)
        
        # Skip CRM update for industry research mode
        if INDUSTRY_RESEARCH_MODE and state["current_lead"].id.startswith("industry_"):
            print("Skipping CRM update for industry research")
            return {"number_leads": state["number_leads"] - 1}
        
        # save new record data, ensure correct fields are used
        new_data = {
            "Status": "ATTEMPTED_TO_CONTACT", # Set lead to attempted contact
            "Score": state["lead_score"], 
            "Analysis Reports": state["reports_folder_link"],
            "Outreach Report": state["custom_outreach_report_link"],
            "Last Contacted": get_current_date()
        }
        self.lead_loader.update_record(state["current_lead"].id, new_data)
        
        # reset reports list
        state["reports"] = []
        
        return {"number_leads": state["number_leads"] - 1}