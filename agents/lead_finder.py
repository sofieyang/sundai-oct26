"""
Lead Finder Agent - FDA Compliance Checker

This agent scrapes web pages from biotech company websites and checks if the content
is FDA compliant for drug product marketing materials.
"""

from google import genai
from google.genai import types
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import re


class LeadFinderAgent:
    """
    Agent that scrapes biotech company websites and checks for FDA compliance
    in drug product marketing materials.
    """

    def __init__(self, api_key: str):
        """
        Initialize the Lead Finder Agent.

        Args:
            api_key: Google AI API key for using Gemini models
        """
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.0-flash-exp"

        # FDA compliance criteria to check
        self.compliance_criteria = [
            "Risk information and side effects disclosure",
            "Balanced presentation of benefits and risks",
            "Substantiation of claims with evidence",
            "Proper indication information",
            "Avoidance of misleading information",
            "Inclusion of important safety information (ISI)",
            "Proper use of approved labeling",
            "Disclosure of off-label use restrictions"
        ]

    def scrape_webpage(self, url: str) -> Optional[Dict[str, str]]:
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

    def check_fda_compliance(self, content: Dict[str, str]) -> Dict:
        """
        Check if the scraped content is FDA compliant using Gemini.

        Args:
            content: Dictionary with webpage content

        Returns:
            Dictionary containing compliance analysis
        """
        prompt = f"""
You are an FDA compliance expert reviewing pharmaceutical marketing materials.

Analyze the following webpage content from a biotech/pharmaceutical company for FDA compliance:

**URL:** {content['url']}
**Title:** {content['title']}

**Content:**
{content['content']}

Please evaluate this content against FDA regulations for drug product promotion, specifically:

1. Risk information and side effects disclosure
2. Balanced presentation of benefits and risks
3. Substantiation of claims with evidence
4. Proper indication information
5. Avoidance of misleading information
6. Inclusion of important safety information (ISI)
7. Proper use of approved labeling
8. Disclosure of off-label use restrictions

Provide your analysis in the following format:

**Compliance Status:** [COMPLIANT / NON-COMPLIANT / NEEDS REVIEW]

**Key Issues Found:**
- [List specific compliance violations or concerns]

**Specific Examples:**
- [Quote specific text that violates FDA regulations]

**Risk Level:** [HIGH / MEDIUM / LOW]

**Recommendations:**
- [What should be corrected]

Be thorough and specific in identifying potential violations.
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=2000,
                )
            )

            analysis_text = response.text

            # Parse the compliance status
            compliance_status = "NEEDS REVIEW"
            if "NON-COMPLIANT" in analysis_text.upper():
                compliance_status = "NON-COMPLIANT"
            elif "COMPLIANT" in analysis_text.upper() and "NON-COMPLIANT" not in analysis_text.upper():
                compliance_status = "COMPLIANT"

            return {
                "url": content['url'],
                "title": content['title'],
                "compliance_status": compliance_status,
                "analysis": analysis_text,
                "content_preview": content['content'][:500]
            }

        except Exception as e:
            print(f"Error analyzing compliance: {str(e)}")
            return {
                "url": content['url'],
                "title": content['title'],
                "compliance_status": "ERROR",
                "analysis": f"Error during analysis: {str(e)}",
                "content_preview": content['content'][:500]
            }

    def find_drug_product_pages(self, base_url: str) -> List[str]:
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

    def analyze_company_website(self, company_url: str) -> List[Dict]:
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


if __name__ == "__main__":
    # Example usage
    import os

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Please set GOOGLE_API_KEY environment variable")
        exit(1)

    agent = LeadFinderAgent(api_key)

    # Example: Analyze a biotech company website
    company_url = "https://example-biotech.com"
    results = agent.analyze_company_website(company_url)

    # Print non-compliant findings
    print("\n" + "="*80)
    print("NON-COMPLIANT FINDINGS:")
    print("="*80)

    for result in results:
        if result['compliance_status'] == "NON-COMPLIANT":
            print(f"\nURL: {result['url']}")
            print(f"Title: {result['title']}")
            print(f"\n{result['analysis']}")
            print("\n" + "-"*80)
