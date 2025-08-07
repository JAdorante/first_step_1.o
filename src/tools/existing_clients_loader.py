# Add this new file: src/tools/existing_clients_loader.py

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.utils import get_google_credentials

class ExistingClientsLoader:
    def __init__(self, spreadsheet_id, sheet_name="Existing Clients"):  # Default to Sheet1
        self.sheet_service = build("sheets", "v4", credentials=get_google_credentials())
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
    
    def get_existing_clients(self):
        """
        Fetches the list of existing client company names from Google Sheets.
        Reads from column B (OEM Sub Account Name).
        
        Returns:
            list: List of company names that are existing clients
        """
        try:
            # Fetch data from the sheet - columns A and B to get the company names
            result = self.sheet_service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id, 
                range=f"{self.sheet_name}!A:B"  # Get both columns A and B
            ).execute()
            
            rows = result.get("values", [])
            
            # Skip header row and extract company names from column B
            existing_clients = []
            for i, row in enumerate(rows):
                if i == 0:  # Skip header row
                    continue
                if len(row) >= 2 and row[1]:  # Check if column B exists and has value
                    company_name = row[1].strip()  # Column B (index 1)
                    if company_name:
                        existing_clients.append(company_name)
            
            print(f"Loaded {len(existing_clients)} existing clients from Google Sheets")
            # Show first few for verification
            if existing_clients:
                print(f"Sample clients: {', '.join(existing_clients[:5])}...")
            
            return existing_clients
            
        except HttpError as e:
            print(f"Error fetching existing clients from Google Sheets: {e}")
            # Return default list if sheet is not accessible
            return ["Genetec", "Nokia", "Siemens", "Google", "Palentir", "Emerson"]
    
    def add_new_client(self, company_name):
        """
        Adds a new client to the existing clients sheet in column B.
        
        Args:
            company_name (str): Name of the company to add
        """
        try:
            # Get current data to find the next empty row
            result = self.sheet_service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id, 
                range=f"{self.sheet_name}!A:B"
            ).execute()
            
            rows = result.get("values", [])
            next_row = len(rows) + 1
            
            # Add the new company in column B
            # You might want to add OEM SBU Level 13 in column A as well
            body = {
                'values': [["", company_name]]  # Empty column A, company name in column B
            }
            
            self.sheet_service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!A{next_row}:B{next_row}",
                valueInputOption="RAW",
                body=body
            ).execute()
            
            print(f"Added {company_name} to existing clients list")
            
        except HttpError as e:
            print(f"Error adding new client to Google Sheets: {e}")