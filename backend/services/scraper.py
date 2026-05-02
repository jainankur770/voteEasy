import requests
from bs4 import BeautifulSoup
import os
import logging

logger = logging.getLogger(__name__)

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "raw_text.txt")

VOTING_URLS = [
    "https://voters.eci.gov.in/",
]

def scrape_and_save(urls: list = VOTING_URLS) -> str:
    """
    Scrapes multiple URLs for voting information and saves it to a raw text file.
    """
    all_text = []
    
    for url in urls:
        try:
            logger.info(f"Scraping {url}...")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Extract text from paragraphs, headers, and list items
            elements = soup.find_all(["p", "h1", "h2", "h3", "li"])
            text_content = " ".join([e.get_text().strip() for e in elements if e.get_text().strip()])
            
            if text_content:
                all_text.append(f"SOURCE: {url}\n{text_content}")
                
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")

    if not all_text:
        # Fallback to default mock data if all scraping fails
        text_content = (
            "Voting is a fundamental right in India. To vote, you must be an Indian citizen and be 18 years "
            "of age or older. You need to register on the electoral roll, which can be done via the Voter Helpline App "
            "or voters.eci.gov.in using Form 6. When voting, carry your EPIC (Voter ID) or an alternative approved "
            "ID like Aadhaar or PAN card. Use the EVM and verify your vote on the VVPAT machine. "
            "For more details, visit the Election Commission of India website."
        )
        all_text.append(text_content)

    final_text = "\n\n".join(all_text)
    
    # Save to data directory
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(final_text)
        
    return final_text

def load_data() -> str:
    """Loads existing raw text data or scrapes it if it doesn't exist."""
    if not os.path.exists(DATA_FILE):
        return scrape_and_save()
    
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    scrape_and_save()
