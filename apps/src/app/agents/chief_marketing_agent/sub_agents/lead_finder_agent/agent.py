from google.adk.agents import LlmAgent 
from google.adk.models.lite_llm import LiteLlm
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup

from .settings import DESCRIPTION, INSTRUCTION

def find_drug_product_pages(base_url: str) -> List[str]:
    """
    Find relevant drug product pages on a company website.

    Args:
        base_url: The company's base website URL

    Returns:
        List of URLs potentially containing drug product information
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find links related to products, pipeline, therapeutics
        keywords = ['product', 'pipeline', 'therapeutic', 'drug', 'medicine',
                    'treatment', 'therapy', 'indication', 'clinical']

        relevant_urls = []
        base_domain = base_url.rstrip('/')

        for link in soup.find_all('a', href=True):
            href = link['href']
            link_text = link.get_text().lower()

            # Check if link contains relevant keywords
            if any(keyword in href.lower() or keyword in link_text for keyword in keywords):
                # Make absolute URL
                if href.startswith('http'):
                    full_url = href
                elif href.startswith('/'):
                    full_url = base_domain + href
                else:
                    full_url = base_domain + '/' + href

                if full_url not in relevant_urls:
                    relevant_urls.append(full_url)

        return relevant_urls[:10]  # Limit to 10 URLs

    except Exception as e:
        print(f"Error finding product pages: {str(e)}")
        return []

def analyze_company_website(company_url: str) -> List[Dict]:
    """
    Main method to analyze a company website for FDA compliance.

    Args:
        company_url: The biotech company's website URL

    Returns:
        List of compliance analysis results for each page
    """
    print(f"Analyzing company website: {company_url}")

    # Find relevant product pages
    print("Finding drug product pages...")
    product_urls = self.find_drug_product_pages(company_url)
    print(f"Found {len(product_urls)} relevant pages")

    # Analyze each page
    results = []
    for url in product_urls:
        print(f"\nAnalyzing: {url}")

        # Scrape the page
        content = self.scrape_webpage(url)
        if not content:
            continue

        # Check compliance
        analysis = self.check_fda_compliance(content)
        results.append(analysis)

        print(f"Status: {analysis['compliance_status']}")

    return results

def scrape_webpage(url: str) -> Optional[Dict[str, str]]:
    """
    Scrape content from a given URL.

    Args:
        url: The webpage URL to scrape

    Returns:
        Dictionary containing the page title, text content, and URL
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text content
        text = soup.get_text(separator='\n', strip=True)

        # Get title
        title = soup.title.string if soup.title else "No title"

        return {
            "url": url,
            "title": title,
            "content": text[:10000]  # Limit content length
        }
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None

agent = LlmAgent(
    model= LiteLlm(model="claude-3-7-sonnet-20250219"),
    name="lead_finder_agent",
    description=DESCRIPTION,
    instruction=INSTRUCTION,
    tools = [find_drug_product_pages, analyze_company_website, scrape_webpage],
    output_key="compliance_analysis"
)
