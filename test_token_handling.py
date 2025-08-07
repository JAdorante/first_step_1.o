#!/usr/bin/env python3
"""
Test script to verify token handling functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
print(sys.path) 
from src.utils import count_tokens, truncate_content_to_fit_tokens

def test_token_counting():
    """Test token counting functionality"""
    print("Testing token counting...")
    
    # Test with a simple string
    test_text = "This is a test string with some content."
    tokens = count_tokens(test_text)
    print(f"Text: '{test_text}'")
    print(f"Token count: {tokens}")
    
    # Test with a longer string
    long_text = "This is a much longer test string that should have more tokens. " * 100
    tokens = count_tokens(long_text)
    print(f"Long text length: {len(long_text)} characters")
    print(f"Token count: {tokens}")
    
    print("Token counting test completed.\n")

def test_content_truncation():
    """Test content truncation functionality"""
    print("Testing content truncation...")
    
    # Create a very long text
    long_text = "This is a sentence. " * 1000
    original_tokens = count_tokens(long_text)
    print(f"Original text tokens: {original_tokens}")
    
    # Truncate to fit within limits
    truncated = truncate_content_to_fit_tokens(long_text, max_tokens=1000)
    truncated_tokens = count_tokens(truncated)
    print(f"Truncated text tokens: {truncated_tokens}")
    print(f"Reduction: {original_tokens - truncated_tokens} tokens")
    
    # Check if truncation notice was added
    if "[Content truncated" in truncated:
        print("✓ Truncation notice was added")
    else:
        print("✗ Truncation notice was not added")
    
    print("Content truncation test completed.\n")

def test_website_scraping():
    """Test website scraping with token limits"""
    print("Testing website scraping...")
    
    try:
        from src.tools.base.markdown_scraper_tool import scrape_website_to_markdown
        
        # Test with a simple website
        test_url = "https://example.com"
        content = scrape_website_to_markdown(test_url, max_length=10000)
        
        tokens = count_tokens(content)
        print(f"Scraped content length: {len(content)} characters")
        print(f"Token count: {tokens}")
        
        if len(content) <= 10000:
            print("✓ Content was properly limited")
        else:
            print("✗ Content was not properly limited")
            
    except Exception as e:
        print(f"Website scraping test failed: {e}")
    
    print("Website scraping test completed.\n")

if __name__ == "__main__":
    print("Running token handling tests...\n")
    
    test_token_counting()
    test_content_truncation()
    test_website_scraping()
    
    print("All tests completed!") 