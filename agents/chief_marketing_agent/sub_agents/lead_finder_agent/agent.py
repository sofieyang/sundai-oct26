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
    product_urls = find_drug_product_pages(company_url)
    print(f"Found {len(product_urls)} relevant pages")

    # Analyze each page
    results = []
    for url in product_urls:
        print(f"\nAnalyzing: {url}")

        # Scrape the page
        content = scrape_webpage(url)
        if not content:
            continue

        # Check compliance
        analysis = check_fda_compliance(content)
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

def check_fda_compliance(content: Dict[str, str]) -> Dict:
    """
    Heuristic FDA compliance check for scraped content.

    Args:
        content: Dict with keys 'url', 'title', 'content'

    Returns:
        Dict containing compliance_status, analysis text, and preview
    """
    text = (content.get("content") or "").lower()

    keywords_risk = [
        "risk",
        "side effect",
        "adverse",
        "safety",
        "important safety information",
        "isi",
    ]
    keywords_benefit = [
        "effective",
        "efficacy",
        "improves",
        "benefit",
        "superior",
        "best in class",
    ]
    keywords_indication = [
        "indication",
        "indicated",
        "for the treatment of",
        "for adults with",
    ]
    keywords_labeling = [
        "prescribing information",
        "labeling",
        "pi",
        "full prescribing",
    ]
    red_flags = [
        "cure",
        "no side effects",
        "guaranteed",
        "safe and effective",
        "miracle",
    ]

    has_risk = any(k in text for k in keywords_risk)
    has_benefit_claims = any(k in text for k in keywords_benefit)
    has_indication = any(k in text for k in keywords_indication)
    has_labeling_ref = any(k in text for k in keywords_labeling)
    has_red_flags = any(k in text for k in red_flags)

    # Determine compliance status
    if has_benefit_claims and not has_risk:
        status = "NON-COMPLIANT"
    elif has_red_flags:
        status = "NON-COMPLIANT"
    elif not has_indication or not has_labeling_ref:
        status = "NEEDS REVIEW"
    else:
        status = "NEEDS REVIEW" if not has_risk else "COMPLIANT"

    issues = []
    if has_benefit_claims and not has_risk:
        issues.append("Benefits presented without adequate risk/side effect disclosure")
    if not has_indication:
        issues.append("Missing or unclear indication information")
    if not has_labeling_ref:
        issues.append("Missing reference to approved labeling / prescribing information")
    if has_red_flags:
        issues.append("Potentially misleading absolute claims (e.g., cure/guaranteed/no side effects)")

    analysis_lines = [
        f"Compliance Status: {status}",
        "Key Issues Found:",
    ]
    analysis_lines += [f"- {i}" for i in (issues or ["No clear issues detected by heuristic check"]) ]

    analysis_text = "\n".join(analysis_lines)

    return {
        "url": content.get("url", ""),
        "title": content.get("title", ""),
        "compliance_status": status,
        "analysis": analysis_text,
        "content_preview": (content.get("content", "")[:500]),
    }

agent = LlmAgent(
    model= LiteLlm(model="claude-3-7-sonnet-20250219"),
    name="lead_finder_agent",
    description=DESCRIPTION,
    instruction=INSTRUCTION,
    tools = [find_drug_product_pages, analyze_company_website, scrape_webpage, check_fda_compliance],
    output_key="compliance_analysis"
)
