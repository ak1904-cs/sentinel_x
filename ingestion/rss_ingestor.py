"""
Public RSS Feed Ingestion Engine for Sentinel-X.
Parses public RSS/Atom feeds and returns lists of AnalysisInput payloads.
"""
import requests
from xml.etree import ElementTree as ET
from typing import List
from models.analysis_models import AnalysisInput
from utils.logging_utils import get_logger

logger = get_logger("rss_ingestor")

def fetch_rss_feed(feed_url: str, max_items: int = 10) -> List[AnalysisInput]:
    """
    Fetch and parse public RSS/Atom feeds.
    Returns a list of AnalysisInput items.
    """
    if not feed_url.startswith("http://") and not feed_url.startswith("https://"):
        feed_url = "https://" + feed_url

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Sentinel-X OSINT FeedIngestor/2.0"
    }

    results = []
    try:
        response = requests.get(feed_url, headers=headers, timeout=10)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        
        # Standard RSS 2.0 channel/item
        items = root.findall(".//item")
        if not items:
            # Atom feed entry fallback
            items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

        for item in items[:max_items]:
            title_elem = item.find("title") or item.find("{http://www.w3.org/2005/Atom}title")
            link_elem = item.find("link") or item.find("{http://www.w3.org/2005/Atom}link")
            desc_elem = item.find("description") or item.find("{http://www.w3.org/2005/Atom}summary") or item.find("{http://www.w3.org/2005/Atom}content")

            title = title_elem.text if title_elem is not None and title_elem.text else "RSS Feed Article"
            link = link_elem.text if link_elem is not None and link_elem.text else feed_url
            if link_elem is not None and not link and "href" in link_elem.attrib:
                link = link_elem.attrib["href"]

            desc = desc_elem.text if desc_elem is not None and desc_elem.text else title
            
            full_content = f"Title: {title}\n\nSummary: {desc}"
            results.append(AnalysisInput(
                source_type="rss",
                content=full_content,
                url_or_reference=link,
                media_type="application/rss+xml",
                metadata={"title": title, "feed_url": feed_url}
            ))

        logger.info(f"Successfully ingested {len(results)} feed articles from {feed_url}")
        return results

    except Exception as e:
        logger.error(f"Failed to fetch RSS feed '{feed_url}': {e}")
        return [AnalysisInput(
            source_type="rss",
            content=f"RSS Ingestion error for feed: {feed_url}. Error: {str(e)}",
            url_or_reference=feed_url,
            media_type="application/rss+xml",
            metadata={"error": str(e)}
        )]
