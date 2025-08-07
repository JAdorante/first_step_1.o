import os
import json
from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.generativeai import GenerativeModel
import tiktoken

# Set the scopes for Google API
SCOPES = [
    # For using GMAIL API
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send',  # Add this for sending emails
    # For using Google sheets as CRM, can comment if using Airtable or other CRM
    'https://www.googleapis.com/auth/spreadsheets',
    # For saving files into Google Docs
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive"
]


def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def get_google_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds
    
def get_report(reports, report_name: str):
    """
    Retrieves the content of a report by its title.
    """
    for report in reports:
        if report.title == report_name:
            return report.content
    return ""

def save_reports_locally(reports):
    # Define the local folder path
    reports_folder = "reports"
    
    # Create folder if it does not exist
    if not os.path.exists(reports_folder):
        os.makedirs(reports_folder)
    
    # Save each report as a file in the folder
    for report in reports:
        file_path = os.path.join(reports_folder, f"{report.title}.txt")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(report.content)

def get_llm_by_provider(llm_provider, model):
    # Find provider
    if llm_provider == "openai":
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model=model, temperature=0.1)
    elif llm_provider == "anthropic":
        # Skip anthropic for now if it's causing issues
        raise ValueError("Anthropic provider not configured for this version")
    elif llm_provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        from google.generativeai import GenerativeModel

        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        client = GenerativeModel(model_name=model)
        llm = ChatGoogleGenerativeAI(
            client=client,
            model=model,
            temperature=0.1
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_provider}")
    return llm

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    Count the number of tokens in a text string.
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        # Fallback: rough estimation (1 token ≈ 4 characters)
        return len(text) // 4

def truncate_content_to_fit_tokens(content: str, max_tokens: int = 12000, model: str = "gpt-3.5-turbo") -> str:
    """
    Truncate content to fit within token limits, preserving important information.
    """
    current_tokens = count_tokens(content, model)
    
    if current_tokens <= max_tokens:
        return content
    
    # Calculate how much we need to reduce
    reduction_ratio = max_tokens / current_tokens
    target_length = int(len(content) * reduction_ratio * 0.9)  # 10% buffer
    
    # Try to truncate intelligently by finding sentence boundaries
    truncated = content[:target_length]
    
    # Find the last complete sentence
    last_period = truncated.rfind('.')
    last_exclamation = truncated.rfind('!')
    last_question = truncated.rfind('?')
    
    last_sentence_end = max(last_period, last_exclamation, last_question)
    
    if last_sentence_end > target_length * 0.8:  # If we found a sentence end in the last 20%
        truncated = truncated[:last_sentence_end + 1]
    
    # Add truncation notice
    truncated += f"\n\n[Content truncated due to length. Original had {current_tokens} tokens, truncated to {count_tokens(truncated, model)} tokens.]"
    
    return truncated

def invoke_llm(
    system_prompt,
    user_message,
    model="gpt-3.5-turbo",
    llm_provider="openai",
    response_format=None,
    max_tokens=12000
):
    # Truncate user message if it's too long
    if isinstance(user_message, str):
        user_message = truncate_content_to_fit_tokens(user_message, max_tokens, model)
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ]  
    
    # Get base llm
    llm = get_llm_by_provider(llm_provider, model)
    
    # For older versions, we'll skip structured output
    if response_format:
        # Just return the raw output for now
        output = llm.invoke(messages)
        # Try to parse it as the expected format
        if hasattr(output, 'content'):
            content = output.content
        else:
            content = str(output)
        
        # Create a mock structured response
        if response_format.__name__ == "WebsiteData":
            return {
                "summary": content[:500] if len(content) > 500 else content,
                "blog_url": "",
                "facebook": "",
                "twitter": "",
                "youtube": ""
            }
        elif response_format.__name__ == "EmailResponse":
            return {
                "subject": "Outreach Opportunity",
                "email": content
            }
        else:
            return content
    else:
        # Use string output parser
        parser = StrOutputParser()
        chain = llm | parser
        output = chain.invoke(messages)
        return output