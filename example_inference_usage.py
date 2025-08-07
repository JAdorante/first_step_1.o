#!/usr/bin/env python3
"""
Example script demonstrating how to use the new inference prompts
to analyze AI startups and infer their infrastructure needs.
"""

import os
from dotenv import load_dotenv
from src.prompts import COMPANY_NEEDS_INFERENCE_PROMPT, QUICK_NEEDS_INFERENCE_PROMPT
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

def analyze_company_needs(company_description, detailed_analysis=True):
    """
    Analyze a company's needs based on their description.
    
    Args:
        company_description (str): Description of the company and what they do
        detailed_analysis (bool): Whether to use detailed or quick inference
    
    Returns:
        str: Analysis results
    """
    
    # Initialize the LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.1
    )
    
    if detailed_analysis:
        # Use the comprehensive inference prompt
        prompt = COMPANY_NEEDS_INFERENCE_PROMPT.format(
            company_description=company_description
        )
    else:
        # Use the quick inference prompt
        prompt = QUICK_NEEDS_INFERENCE_PROMPT.format(
            company_description=company_description
        )
    
    # Generate the analysis
    response = llm.invoke(prompt)
    return response.content

def main():
    """
    Example usage of the inference prompts with different types of AI companies.
    """
    
    # Example 1: Computer Vision Startup
    computer_vision_company = """
    VisionAI is a Series A startup developing real-time computer vision solutions 
    for manufacturing quality control. They process 10,000+ images per hour across 
    50+ factory locations globally. Their AI models detect defects with 99.2% accuracy 
    and are deployed on edge devices in harsh industrial environments. They serve 
    Fortune 500 manufacturers and are experiencing 300% year-over-year growth.
    They recently raised $15M in Series A funding and have 35 employees.
    """
    
    print("=== COMPUTER VISION STARTUP ANALYSIS ===")
    print("Company: VisionAI")
    print("Description:", computer_vision_company.strip())
    print("\n--- QUICK INFERENCE ---")
    quick_analysis = analyze_company_needs(computer_vision_company, detailed_analysis=False)
    print(quick_analysis)
    
    print("\n--- DETAILED INFERENCE ---")
    detailed_analysis = analyze_company_needs(computer_vision_company, detailed_analysis=True)
    print(detailed_analysis)
    
    print("\n" + "="*80 + "\n")
    
    # Example 2: LLM Startup
    llm_company = """
    TextGenAI is a seed-stage startup building large language models for 
    enterprise document processing. They train custom LLMs on client data 
    and provide API access for document analysis, summarization, and 
    information extraction. They have 25 enterprise customers and process 
    millions of documents monthly. Their models require significant GPU 
    resources for training and inference. They raised $2.5M in seed funding 
    and have 8 employees.
    """
    
    print("=== LLM STARTUP ANALYSIS ===")
    print("Company: TextGenAI")
    print("Description:", llm_company.strip())
    print("\n--- QUICK INFERENCE ---")
    quick_analysis = analyze_company_needs(llm_company, detailed_analysis=False)
    print(quick_analysis)
    
    print("\n--- DETAILED INFERENCE ---")
    detailed_analysis = analyze_company_needs(llm_company, detailed_analysis=True)
    print(detailed_analysis)
    
    print("\n" + "="*80 + "\n")
    
    # Example 3: Healthcare AI Startup
    healthcare_company = """
    MedAI Solutions is a Series B healthcare AI company developing 
    diagnostic assistance tools for radiologists. They process medical 
    images and provide real-time analysis to help doctors detect 
    abnormalities. They serve 200+ hospitals across the US and Europe, 
    processing 50,000+ medical images daily. They require HIPAA compliance 
    and data sovereignty for different regions. They raised $45M in Series B 
    funding and have 150 employees.
    """
    
    print("=== HEALTHCARE AI STARTUP ANALYSIS ===")
    print("Company: MedAI Solutions")
    print("Description:", healthcare_company.strip())
    print("\n--- QUICK INFERENCE ---")
    quick_analysis = analyze_company_needs(healthcare_company, detailed_analysis=False)
    print(quick_analysis)
    
    print("\n--- DETAILED INFERENCE ---")
    detailed_analysis = analyze_company_needs(healthcare_company, detailed_analysis=True)
    print(detailed_analysis)
    
    print("\n" + "="*80 + "\n")
    
    # Example 4: Series C+ Company
    series_c_company = """
    DataFlow Analytics is a Series C company that provides enterprise 
    data processing and analytics platforms. They serve Fortune 500 
    companies globally with real-time data streaming and AI-powered 
    insights. They have 500+ employees across 15 countries and process 
    petabytes of data daily. They recently raised $150M in Series C 
    funding and are valued at $2.5B.
    """
    
    print("=== SERIES C+ COMPANY ANALYSIS ===")
    print("Company: DataFlow Analytics")
    print("Description:", series_c_company.strip())
    print("\n--- QUICK INFERENCE ---")
    quick_analysis = analyze_company_needs(series_c_company, detailed_analysis=False)
    print(quick_analysis)
    
    print("\n--- DETAILED INFERENCE ---")
    detailed_analysis = analyze_company_needs(series_c_company, detailed_analysis=True)
    print(detailed_analysis)

if __name__ == "__main__":
    main() 