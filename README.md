# First Step 1.o

An intelligent lead research and outreach automation system that leverages AI to analyze companies, score leads, and generate personalized outreach materials at scale.

## 🚀 Overview

This system automates the entire outreach process by:
- Discovering new companies in target industries
- Researching companies and decision makers via LinkedIn, websites, and news
- Scoring leads based on multiple criteria
- Generating personalized outreach reports, emails, and interview scripts
- Managing processed companies to avoid duplicates
- Integrating with CRM systems (Airtable, Google Sheets, HubSpot)


## ✨ Features

### Core Capabilities
- **Multi-source Lead Discovery**: Find companies via CRM or industry-based research
- **Comprehensive Research**: LinkedIn profiles, company websites, blogs, social media, news
- **AI-Powered Analysis**: Uses GPT-3.5/GPT-4 for intelligent content analysis
- **Lead Scoring**: 10-point scoring system based on viability, technical fit, and partnership potential
- **Automated Outreach**: Generates personalized emails and interview scripts
- **Duplicate Prevention**: Tracks processed companies to avoid redundant outreach
- **Multi-CRM Support**: Integrates with Airtable, Google Sheets, and HubSpot

### Research Capabilities
- LinkedIn profile scraping (personal and company)
- Website content analysis and tech stack inference
- Blog content analysis for thought leadership assessment
- YouTube channel analysis for engagement metrics
- Recent news monitoring (last 6 months)
- Social media presence evaluation

### Output Generation
- Comprehensive lead research reports
- Digital presence analysis reports
- Custom outreach strategy documents
- Personalized email templates
- SPIN-based interview scripts
- All reports saved to Google Docs with shareable links

## 🏗️ System Architecture

### State Graph Flow
```
1. Get New Leads → 2. Check for Remaining Leads
                    ↓
3. Fetch LinkedIn Data → 4. Review Company Website → 5. Collect Company Info
                                                      ↓
6. Parallel Analysis: Blog, Social Media, News → 7. Generate Reports
                                                  ↓
8. Score Lead → 9. Check Qualification
                 ↓ (if qualified)
10. Generate Outreach Materials → 11. Create Email & Script
                                   ↓
12. Save to Google Docs → 13. Update CRM → Loop to Step 2
```

### Key Components
- **Graph Engine**: LangGraph for orchestrating the workflow
- **LLM Integration**: OpenAI GPT models for content analysis
- **Data Storage**: Local JSON for processed companies, Google Docs for reports
- **Web Scraping**: BeautifulSoup for content extraction
- **APIs**: LinkedIn (via RapidAPI), Google Search (Serper), YouTube Data API

## 📦 Prerequisites

### Required Accounts & API Keys
1. **OpenAI API** - For GPT-3.5/GPT-4 access
2. **Google Cloud** - For Google Docs, Sheets, and Gmail APIs
3. **Serper API** - For web search functionality
4. **RapidAPI** - For LinkedIn scraping
5. **YouTube API** - For channel analytics (optional)
6. **CRM Access** - Airtable, Google Sheets, or HubSpot

### Python Requirements
- Python 3.8 or higher
- pip package manager

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd outreach-automation
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up Google OAuth**
   - Create a project in Google Cloud Console
   - Enable APIs: Google Docs, Google Drive, Gmail, Google Sheets
   - Create OAuth 2.0 credentials
   - Download as `credentials.json` and place in project root

5. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

## ⚙️ Configuration

### Environment Variables (.env)
```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Google APIs (optional if using OAuth)
GOOGLE_API_KEY=your_google_api_key

# Search and Scraping
SERPER_API_KEY=your_serper_api_key
RAPIDAPI_KEY=your_rapidapi_key

# YouTube (optional)
YOUTUBE_API_KEY=your_youtube_api_key

# CRM Configuration (choose one)
# Airtable
AIRTABLE_ACCESS_TOKEN=your_airtable_token
AIRTABLE_BASE_ID=your_base_id
AIRTABLE_TABLE_NAME=your_table_name

# Google Sheets
SHEET_ID=your_google_sheet_id

# HubSpot
HUBSPOT_API_KEY=your_hubspot_key

# Existing Clients Sheet (optional)
EXISTING_CLIENTS_SHEET_ID=your_existing_clients_sheet_id
```

### Configuration Flags (src/nodes.py)
```python
SEND_EMAIL_DIRECTLY = True  # Auto-send emails or save as draft
SEND_EMAIL_TO_LINKEDIN_PERSON = True  # Email decision makers if public email found
SAVE_TO_GOOGLE_DOCS = True  # Save reports to Google Docs
INDUSTRY_RESEARCH_MODE = True  # Find new companies by industry
STOP_AFTER_FIRST_QUALIFIED = True  # Process one qualified lead at a time
```

### Industries to Research
Edit `INDUSTRIES_TO_RESEARCH` in `src/nodes.py`:
```python
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
```

## 🚀 Usage

### Basic Usage
```bash
python main.py
```

### Industry Research Mode
The system can operate in two modes:

1. **Standard Mode**: Processes leads from your CRM
2. **Industry Research Mode**: Discovers new companies in specified industries

Toggle via `INDUSTRY_RESEARCH_MODE` in `src/nodes.py`.

### Managing Processed Companies

View processed companies:
```bash
python manage_company_log.py view
```

Search for a specific company:
```bash
python manage_company_log.py search "Microsoft"
```

Get LinkedIn links for a company:
```bash
python manage_company_log.py linkedin "Microsoft"
```

Clear the log (use with caution):
```bash
python manage_company_log.py clear
```

Export the log:
```bash
python manage_company_log.py export my_backup.json
```

## 📊 Lead Scoring

The system scores leads on a 0-10 scale based on:

### Scoring Categories
1. **Company Viability (25%)**
   - Business model clarity
   - Market need
   - Competitive position
   - Growth potential

2. **Technical Assessment (25%)**
   - Technology quality
   - Technical team strength
   - Product maturity
   - Innovation level

3. **Market Opportunity (20%)**
   - Market size
   - Customer demand
   - Industry trends
   - Geographic reach

4. **Partnership Potential (20%)**
   - Strategic fit
   - Collaboration potential
   - Resource needs
   - Mutual value creation

5. **Risk Assessment (10%)**
   - Financial stability
   - Execution risk
   - Market risk
   - Competitive risk

**Qualification Threshold**: Leads scoring ≥5.0 are considered qualified.

## 📄 Output Reports

### Report Types
1. **General Lead Research Report** - Overview of lead and company
2. **Digital Presence Report** - Analysis of online presence
3. **Global Lead Analysis Report** - Comprehensive assessment
4. **Custom Outreach Report** - Tailored partnership proposal
5. **Personalized Email** - Ready-to-send outreach email
6. **Interview Script** - SPIN-based discovery questions

### Report Storage
- **Local**: Saved in `reports/` directory
- **Google Docs**: Organized in folders by lead/company name
- **Shareable Links**: Generated for each report

## 🔌 API Integrations

### LinkedIn Scraping
Uses RapidAPI's LinkedIn service for profile data:
- Personal profiles: `/get-linkedin-profile`
- Company profiles: `/get-company-by-linkedinurl`

### Web Search
Serper API for:
- Company discovery
- News articles
- Website finding
- Decision maker search

### Google Services
- **Docs API**: Report creation and sharing
- **Drive API**: Folder management
- **Gmail API**: Email drafting and sending
- **Sheets API**: CRM integration

## 🐛 Troubleshooting

### Common Issues

**1. Token Limit Errors**
```bash
# Test token handling
python test_token_handling.py
```
Solution: The system automatically truncates content exceeding token limits.

**2. Google Authentication Issues**
- Delete `token.json` and re-authenticate
- Ensure all required Google APIs are enabled
- Check OAuth consent screen configuration

**3. LinkedIn Scraping Failures**
- Verify RapidAPI key is valid
- Check if LinkedIn URL format is correct
- Some profiles may be private or restricted

**4. CRM Connection Issues**
- Verify API credentials
- Check table/sheet permissions
- Ensure correct field names in CRM

### Debug Mode
Add to your script for detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔧 Development

### Project Structure
```
outreach-automation/
├── src/
│   ├── graph.py              # Workflow orchestration
│   ├── nodes.py              # Node implementations
│   ├── state.py              # State definitions
│   ├── prompts.py            # AI prompt templates
│   ├── structured_outputs.py # Output schemas
│   ├── utils.py              # Helper functions
│   └── tools/                # Integration tools
│       ├── base/             # Core tools
│       ├── leads_loader/     # CRM integrations
│       └── other tools...
├── data/
│   └── case_studies/         # RAG content
├── reports/                  # Local report storage
├── main.py                   # Entry point
├── manage_company_log.py     # Log management
└── processed_companies.json  # Processed company tracking
```

### Adding New Features

**1. New CRM Integration**
- Create new class in `src/tools/leads_loader/`
- Extend `LeadLoaderBase`
- Implement `fetch_records()` and `update_record()`

**2. New Analysis Type**
- Add analysis node in `src/nodes.py`
- Update graph in `src/graph.py`
- Create prompt in `src/prompts.py`

**3. New Industry**
- Add to `INDUSTRIES_TO_RESEARCH` list
- System will automatically include in research

### Testing
```bash
# Run token handling tests
python test_token_handling.py

# Test specific component
python -m pytest tests/test_component.py
```

## 📝 License

Dell Technologies © 2025


## 📧 Support

For issues and questions:
- Contact jadorant@villanova.edu for questions
- Review processed_companies.json for system state
- Enable debug logging for detailed error messages

---

**Note**: This system is designed for B2B outreach automation. Ensure compliance with all applicable laws and regulations regarding automated outreach and data collection in your jurisdiction.
