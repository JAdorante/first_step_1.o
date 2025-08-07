import os
from dotenv import load_dotenv
from src.graph import OutReachAutomation
from src.state import *
from src.tools.leads_loader.airtable import AirtableLeadLoader
from src.tools.leads_loader.google_sheets import GoogleSheetLeadLoader

# Load environment variables from a .env file
load_dotenv()

if __name__ == "__main__":
    # Use Airtable for accessing your leads list
    lead_loader = AirtableLeadLoader(
        access_token=os.getenv("AIRTABLE_ACCESS_TOKEN"),
        base_id=os.getenv("AIRTABLE_BASE_ID"),
        table_name=os.getenv("AIRTABLE_TABLE_NAME"),
    )
    
    # Use Sheet for accessing your leads list
    #lead_loader = GoogleSheetLeadLoader(
         #spreadsheet_id=os.getenv("SHEET_ID"),
    # )
    
    # Get the existing clients sheet ID from environment or set it directly
    existing_clients_sheet_id = os.getenv("EXISTING_CLIENTS_SHEET_ID")  # Add this to your .env file
    
    # Instantiate the OutReachAutomation class with existing clients sheet
    automation = OutReachAutomation(lead_loader, existing_clients_sheet_id)
    app = automation.app
    
    # initial graph inputs:
    # Lead ids to be processed, leave empty to fetch all new leads

    # If GraphState expects a dictionary or specific structure, adjust accordingly.
    # Here, we assume GraphState takes a dictionary as a single argument.
    inputs = {
    "leads_ids": [],
    "leads_data": [],
    "current_lead": LeadData(
        id="",
        name="",
        address="",
        email="",
        phone="",
        profile=""
    ),
    "lead_score": "",
    "company_data": CompanyData(),
    "reports": [],
    "reports_folder_link": "",
    "custom_outreach_report_link": "",
    "personalized_email": "",
    "interview_script": "",
    "number_leads": 0
        }

    # Run the outreach automation with the provided lead name and email
    # Ensure inputs are wrapped in GraphState if required by the app
    state = GraphState(**inputs)
    
    # Increase recursion limit since we're processing multiple industries
    import sys
    sys.setrecursionlimit(2000)  # or higher, but not lower than 1000

    output = app.invoke(state)
      # instead of app.invoke(state)
    print(output)