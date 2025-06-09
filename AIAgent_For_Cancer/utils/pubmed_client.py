"""
PubMed API client for the Oncology AI Assistant System.
Provides functionality to search and retrieve articles from PubMed.
"""
import logging
import requests
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from requests.exceptions import RequestException, ConnectionError, Timeout

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PubMedClient:
    """Client for interacting with the PubMed API."""
    
    def __init__(self, api_key: str = None):
        """Initialize the PubMed API client.
        
        Args:
            api_key: Optional API key for higher rate limits
        """
        # Base URL for NCBI E-utilities
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.api_key = api_key
        
    def search(self, query: str, max_results: int = 20, days_lookback: int = 30) -> List[Dict[str, Any]]:
        """Search for articles matching the query.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            days_lookback: Number of days to look back
            
        Returns:
            List of article dictionaries
        """
        logger.info(f"Searching PubMed for: {query}")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_lookback)
        
        # Format dates for PubMed API
        date_range = f"{start_date.strftime('%Y/%m/%d')}:{end_date.strftime('%Y/%m/%d')}[pdat]"
        
        # Construct search query with date range
        full_query = f"({query}) AND {date_range}"
        
        try:
            # First, search for article IDs
            search_url = f"{self.base_url}esearch.fcgi"
            params = {
                "db": "pubmed",
                "term": full_query,
                "retmax": max_results,
                "sort": "date",
                "retmode": "json"
            }
            
            if self.api_key:
                params["api_key"] = self.api_key
                
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            search_data = response.json()
            
            # Extract article IDs
            id_list = search_data.get("esearchresult", {}).get("idlist", [])
            
            if not id_list:
                logger.info(f"No results found for query: {query}")
                return []
                
            logger.info(f"Found {len(id_list)} articles matching query: {query}")
            
            # Fetch article details
            articles = []
            
            # Process in batches to avoid API limits
            batch_size = 20
            for i in range(0, len(id_list), batch_size):
                batch_ids = id_list[i:i+batch_size]
                batch_articles = self._fetch_articles(batch_ids)
                articles.extend(batch_articles)
                
                # Respect API rate limits
                if i + batch_size < len(id_list):
                    time.sleep(0.5)
                    
            return articles
            
        except Exception as e:
            logger.error(f"Error searching PubMed: {e}")
            return []
    
    def _fetch_articles(self, id_list: List[str]) -> List[Dict[str, Any]]:
        """Fetch details for a list of article IDs.
        
        Args:
            id_list: List of PubMed IDs
            
        Returns:
            List of article dictionaries
        """
        if not id_list:
            return []
            
        try:
            # Fetch article details using efetch
            fetch_url = f"{self.base_url}efetch.fcgi"
            params = {
                "db": "pubmed",
                "id": ",".join(id_list),
                "retmode": "xml"
            }
            
            if self.api_key:
                params["api_key"] = self.api_key
                
            response = requests.get(fetch_url, params=params)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.text)
            
            # Extract article information
            articles = []
            
            for article_elem in root.findall(".//PubmedArticle"):
                article = self._parse_article(article_elem)
                if article:
                    articles.append(article)
                    
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching article details: {e}")
            return []
    
    def _parse_article(self, article_elem: ET.Element) -> Optional[Dict[str, Any]]:
        """Parse article information from XML element.
        
        Args:
            article_elem: XML element containing article information
            
        Returns:
            Dictionary with article information
        """
        try:
            # Extract PubMed ID
            pmid_elem = article_elem.find(".//PMID")
            if pmid_elem is None:
                return None
                
            pmid = pmid_elem.text
            
            # Extract article information
            article = article_elem.find(".//Article")
            
            if article is None:
                return None
                
            # Extract title
            title_elem = article.find("./ArticleTitle")
            title = title_elem.text if title_elem is not None else "Unknown Title"
            
            # Extract journal information
            journal_elem = article.find("./Journal")
            journal = "Unknown Journal"
            
            if journal_elem is not None:
                journal_title = journal_elem.find("./Title")
                if journal_title is not None:
                    journal = journal_title.text
                    
            # Extract publication date
            pub_date_elem = article_elem.find(".//PubDate")
            pub_date = "Unknown Date"
            
            if pub_date_elem is not None:
                year = pub_date_elem.find("./Year")
                month = pub_date_elem.find("./Month")
                day = pub_date_elem.find("./Day")
                
                date_parts = []
                
                if year is not None:
                    date_parts.append(year.text)
                    
                if month is not None:
                    date_parts.append(month.text)
                    
                if day is not None:
                    date_parts.append(day.text)
                    
                if date_parts:
                    pub_date = "/".join(date_parts)
                    
            # Extract authors
            authors = []
            author_list = article.find("./AuthorList")
            
            if author_list is not None:
                for author_elem in author_list.findall("./Author"):
                    last_name = author_elem.find("./LastName")
                    fore_name = author_elem.find("./ForeName")
                    
                    author_name = ""
                    
                    if last_name is not None:
                        author_name = last_name.text
                        
                    if fore_name is not None:
                        if author_name:
                            author_name = f"{fore_name.text} {author_name}"
                        else:
                            author_name = fore_name.text
                            
                    if author_name:
                        authors.append(author_name)
                        
            # Extract abstract
            abstract_elem = article.find(".//Abstract")
            abstract = ""
            
            if abstract_elem is not None:
                abstract_texts = abstract_elem.findall("./AbstractText")
                
                for abstract_text in abstract_texts:
                    label = abstract_text.get("Label")
                    text = abstract_text.text or ""
                    
                    if label:
                        abstract += f"{label}: {text}\n\n"
                    else:
                        abstract += f"{text}\n\n"
                        
            # Extract keywords
            keywords = []
            keyword_list = article_elem.find(".//KeywordList")
            
            if keyword_list is not None:
                for keyword_elem in keyword_list.findall("./Keyword"):
                    if keyword_elem.text:
                        keywords.append(keyword_elem.text)
                        
            # Return article information
            return {
                "pmid": pmid,
                "title": title,
                "journal": journal,
                "publication_date": pub_date,
                "authors": authors,
                "abstract": abstract.strip(),
                "keywords": keywords,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            }
            
        except Exception as e:
            logger.error(f"Error parsing article: {e}")
            return None
    
    def get_article(self, pmid: str) -> Optional[Dict[str, Any]]:
        """Get article details by PubMed ID.
        
        Args:
            pmid: PubMed ID
            
        Returns:
            Dictionary with article information
        """
        articles = self._fetch_articles([pmid])
        return articles[0] if articles else None
