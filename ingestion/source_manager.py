"""
Source Manager Router for Sentinel-X Ingestion Layer.
Inspects source input strings/URLs and dispatches to Web, RSS, or API ingestors.
"""
from typing import List
from models.analysis_models import AnalysisInput
from ingestion.web_ingestor import fetch_public_webpage
from ingestion.rss_ingestor import fetch_rss_feed
from ingestion.api_ingestor import fetch_api_source

class SourceManager:
    @staticmethod
    def ingest_source(source_input: str, source_type: str = "auto") -> List[AnalysisInput]:
        """
        Inspect source_input and route to appropriate ingestion handler.
        Returns a list of AnalysisInput payloads.
        """
        source_input = source_input.strip()
        if not source_input:
            return []

        # Auto-detect RSS feed URL
        if source_type == "rss" or any(k in source_input.lower() for k in [".rss", ".xml", "/feed", "/rss"]):
            return fetch_rss_feed(source_input)
            
        # Web Page URL
        elif source_type == "web" or source_input.startswith("http://") or source_input.startswith("https://") or "www." in source_input:
            return [fetch_public_webpage(source_input)]
            
        # API Source
        elif source_type == "api":
            return [fetch_api_source(source_input)]
            
        # Raw Text Payload Fallback
        else:
            return [AnalysisInput(
                source_type="text",
                content=source_input,
                url_or_reference="User Direct Input",
                media_type="text/plain"
            )]
