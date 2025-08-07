import re
import html2text
import requests
from bs4 import BeautifulSoup
import time

def scrape_website_to_markdown(url: str, max_length: int = 50000) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }

    # Make the HTTP request
    try:
        response = requests.get(url, headers=headers, timeout=30)
    except requests.RequestException as e:
        raise Exception(f"Request failed: {e}")

    if response.status_code == 403:
        raise Exception(f"Access forbidden (HTTP 403) when fetching the URL. The website may be blocking automated requests. Try accessing the site manually or using a different network/user-agent.")
    elif response.status_code != 200:
        raise Exception(f"Failed to fetch the URL. Status code: {response.status_code}")

    # Parse the HTML
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Remove script and style elements to reduce content
    for script in soup(["script", "style", "nav", "footer", "header"]):
        script.decompose()
    
    # Extract main content areas (prioritize main content over navigation/footer)
    main_content = ""
    
    # Look for main content areas
    main_selectors = [
        'main',
        '[role="main"]',
        '.main-content',
        '.content',
        '#content',
        '#main',
        'article',
        '.article'
    ]
    
    for selector in main_selectors:
        elements = soup.select(selector)
        if elements:
            main_content = str(elements[0])
            break
    
    # If no main content found, use body but filter out navigation/footer
    if not main_content:
        body = soup.find('body')
        if body:
            # Remove navigation and footer elements
            for element in body.find_all(['nav', 'footer', 'header', 'aside']):
                element.decompose()
            main_content = str(body)
        else:
            main_content = soup.prettify()
    
    # Convert HTML to markdown
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = True
    h.ignore_tables = True
    h.body_width = 0  # Don't wrap text
    markdown_content = h.handle(main_content)

    # Clean up excess newlines and whitespace
    markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)
    markdown_content = re.sub(r" +", " ", markdown_content)
    markdown_content = markdown_content.strip()
    
    # Truncate if content is too long
    if len(markdown_content) > max_length:
        # Try to truncate at a sentence boundary
        truncated = markdown_content[:max_length]
        last_period = truncated.rfind('.')
        last_exclamation = truncated.rfind('!')
        last_question = truncated.rfind('?')
        
        last_sentence_end = max(last_period, last_exclamation, last_question)
        
        if last_sentence_end > max_length * 0.8:
            markdown_content = truncated[:last_sentence_end + 1]
        else:
            markdown_content = truncated
        
        markdown_content += f"\n\n[Content truncated due to length. Original was {len(markdown_content)} characters.]"

    return markdown_content