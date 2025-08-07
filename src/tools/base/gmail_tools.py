import base64
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from src.utils import get_google_credentials

class GmailTools:
    def __init__(self):
        self.service = build('gmail', 'v1', credentials=get_google_credentials())

    def create_draft_email(self, recipient, subject, email_content):
        try:
            message = self._create_message(recipient, subject, email_content)
            draft = self.service.users().drafts().create(userId='me', body={
                'message': {
                    'raw': self._encode_message(message)
                }
            }).execute()
            print(f"Draft created for email for {recipient} with subject '{subject}'")
            return draft
        except Exception as error:
            print(f"An error occurred while creating draft: {error}")
            return None
        
    def send_email(self, recipient, subject, email_content):
        try:
            print(f"DEBUG: Attempting to send email to {recipient}")
            print(f"DEBUG: Subject: {subject}")
            print(f"DEBUG: Content length: {len(email_content) if email_content else 0}")
            
            message = self._create_message(recipient, subject, email_content)
            print(f"DEBUG: Created message object")
            
            encoded_message = self._encode_message(message)
            print(f"DEBUG: Encoded message successfully")
            
            sent_message = self.service.users().messages().send(userId='me', body={
                'raw': encoded_message
            }).execute()
            
            print(f"Email sent to {recipient} with subject '{subject}'")
            print(f"DEBUG: Gmail API response: {sent_message}")
            return sent_message
        except Exception as error:
            print(f"An error occurred while sending reply: {error}")
            print(f"DEBUG: Error type: {type(error).__name__}")
            print(f"DEBUG: Error details: {str(error)}")
            return None

    def _create_message(self, recipient, subject, text):
        message = MIMEText(text)
        message['to'] = recipient
        message['subject'] = subject
        return message

    def _encode_message(self, message):
        return base64.urlsafe_b64encode(message.as_bytes()).decode()