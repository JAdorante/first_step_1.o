#!/usr/bin/env python3
"""
Utility script to manage the processed companies log.
This script helps you view, clear, and export the log of companies that have been processed.
"""

import json
import os
import sys
from datetime import datetime

def load_processed_companies(filename="processed_companies.json"):
    """Load processed companies from JSON file"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                return data.get('companies', [])
        else:
            print(f"Log file {filename} does not exist.")
            return []
    except Exception as e:
        print(f"Error loading log file: {e}")
        return []

def save_processed_companies(companies, filename="processed_companies.json"):
    """Save processed companies to JSON file"""
    try:
        data = {
            'last_updated': datetime.now().isoformat(),
            'companies': companies
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Log saved to {filename}")
    except Exception as e:
        print(f"Error saving log file: {e}")

def view_log():
    """Display the processed companies log"""
    companies = load_processed_companies()
    
    if not companies:
        print("No companies have been processed yet.")
        return
    
    print(f"\n=== Processed Companies Log ===")
    print(f"Total companies: {len(companies)}")
    
    # Group by industry
    industry_groups = {}
    for company in companies:
        industry = company.get('industry', 'Unknown')
        if industry not in industry_groups:
            industry_groups[industry] = []
        industry_groups[industry].append(company)
    
    for industry, company_list in industry_groups.items():
        print(f"\n--- {industry} ({len(company_list)} companies) ---")
        for company in company_list:
            date = company['processed_date'][:10] if company['processed_date'] else 'Unknown'
            print(f"  • {company['name']} - {date}")

def clear_log():
    """Clear the processed companies log"""
    response = input("Are you sure you want to clear the processed companies log? (y/N): ")
    if response.lower() == 'y':
        save_processed_companies([])
        print("Log cleared successfully.")
    else:
        print("Operation cancelled.")

def export_log(filename=None):
    """Export the processed companies log"""
    companies = load_processed_companies()
    
    if not filename:
        filename = f"processed_companies_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(companies, f, indent=2)
        print(f"Log exported to {filename}")
    except Exception as e:
        print(f"Error exporting log: {e}")

def search_company(company_name):
    """Search for a specific company in the log"""
    companies = load_processed_companies()
    
    if not companies:
        print("No companies in log.")
        return
    
    found = False
    normalized_search = company_name.lower().strip()
    
    for company in companies:
        if normalized_search in company['name'].lower():
            print(f"\nFound: {company['name']}")
            print(f"  Industry: {company.get('industry', 'N/A')}")
            print(f"  Company LinkedIn: {company.get('linkedin_url', 'N/A')}")
            print(f"  Decision Maker LinkedIn: {company.get('decision_maker_linkedin', 'N/A')}")
            print(f"  Processed: {company.get('processed_date', 'N/A')}")
            found = True
    
    if not found:
        print(f"No companies found matching '{company_name}'")

def get_linkedin_links(company_name):
    """Get LinkedIn links for a specific company"""
    companies = load_processed_companies()
    
    if not companies:
        print("No companies in log.")
        return
    
    normalized_search = company_name.lower().strip()
    
    for company in companies:
        if normalized_search in company['name'].lower():
            print(f"\n🔗 LinkedIn Links for {company['name']}:")
            
            if company.get('linkedin_url'):
                print(f"  🏢 Company: {company['linkedin_url']}")
            else:
                print(f"  🏢 Company: Not available")
                
            if company.get('decision_maker_linkedin'):
                print(f"  👤 Decision Maker: {company['decision_maker_linkedin']}")
            else:
                print(f"  👤 Decision Maker: Not available")
            
            return
    
    print(f"Company '{company_name}' not found in log")

def show_help():
    """Show help information"""
    print("""
Processed Companies Log Manager

Usage: python manage_company_log.py [command]

Commands:
  view              - View all processed companies (grouped by industry)
  clear             - Clear the processed companies log
  export [filename] - Export the log to a JSON file
  search <name>     - Search for a specific company
  linkedin <name>   - Get LinkedIn links for a specific company
  help              - Show this help message

Examples:
  python manage_company_log.py view
  python manage_company_log.py export my_export.json
  python manage_company_log.py search "Microsoft"
  python manage_company_log.py linkedin "Microsoft"
""")

def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "view":
        view_log()
    elif command == "clear":
        clear_log()
    elif command == "export":
        filename = sys.argv[2] if len(sys.argv) > 2 else None
        export_log(filename)
    elif command == "search":
        if len(sys.argv) < 3:
            print("Please provide a company name to search for.")
            return
        company_name = sys.argv[2]
        search_company(company_name)
    elif command == "linkedin":
        if len(sys.argv) < 3:
            print("Please provide a company name to get LinkedIn links for.")
            return
        company_name = sys.argv[2]
        get_linkedin_links(company_name)
    elif command == "help":
        show_help()
    else:
        print(f"Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main() 