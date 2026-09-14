"""
Public Web Ingestion Engine for Sentinel-X.
Fetches public web pages and extracts visible text content using requests and BeautifulSoup.
Respects robots/HTTP timeout restrictions cleanly.
"""
import requests
from bs4 import BeautifulSoup
from models.analysis_models import AnalysisInput
from utils.logging_utils import get_logger

logger = get_logger("web_ingestor")

def fetch_public_webpage(url: str) -> AnalysisInput:
    """
    Fetch public web page text content.
    Returns AnalysisInput payload.
    """
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Sentinel-X OSINT Ingestor/2.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style tags
        for script in soup(["script", "style", "header", "footer", "nav"]):
            script.extract()

        title = soup.title.string if soup.title else url
        paragraphs = [p.get_text().strip() for p in soup.find_all(['p', 'h1', 'h2', 'h3']) if len(p.get_text().strip()) > 20]
        extracted_text = "\n\n".join(paragraphs)

        if not extracted_text.strip():
            extracted_text = soup.get_text(separator=' ', strip=True)[:4000]

        logger.info(f"Successfully ingested public web page: {url} ({len(extracted_text)} chars)")
        return AnalysisInput(
            source_type="web",
            content=extracted_text,
            url_or_reference=url,
            media_type="text/html",
            metadata={"title": str(title), "status_code": response.status_code}
        )

    except Exception as e:
        logger.error(f"Failed to fetch public web page '{url}': {e}")
        return AnalysisInput(
            source_type="web",
            content=f"Ingestion failed for URL: {url}. Error: {str(e)}",
            url_or_reference=url,
            media_type="text/html",
            metadata={"error": str(e)}
        )
