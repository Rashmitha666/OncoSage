"""
Document parser for the Oncology AI Assistant System.
Provides functionality to parse and extract content from medical documents.
"""
import logging
import os
import re
import requests
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PDFParser:
    """Parser for PDF documents."""
    
    def __init__(self):
        """Initialize the PDF parser."""
        self.supported_extensions = ['.pdf']
        
    def parse(self, file_path: str) -> Dict[str, Any]:
        """Parse a PDF document.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing parsed document content
        """
        logger.info(f"Parsing PDF document: {file_path}")
        
        try:
            # In a real implementation, this would use a PDF parsing library like PyPDF2 or pdfminer
            # For demonstration purposes, we'll return placeholder data
            return {
                'title': os.path.basename(file_path).replace('.pdf', ''),
                'authors': ['Unknown Author'],
                'date': 'Unknown Date',
                'content': 'PDF content would be extracted here.',
                'sections': {
                    'abstract': 'Abstract would be extracted here.',
                    'introduction': 'Introduction would be extracted here.',
                    'methods': 'Methods would be extracted here.',
                    'results': 'Results would be extracted here.',
                    'discussion': 'Discussion would be extracted here.',
                    'conclusion': 'Conclusion would be extracted here.',
                    'references': ['Reference 1', 'Reference 2']
                }
            }
            
        except Exception as e:
            logger.error(f"Error parsing PDF document: {e}")
            return {
                'title': os.path.basename(file_path),
                'content': '',
                'error': str(e)
            }


class TextParser:
    """Parser for plain text documents."""
    
    def __init__(self):
        """Initialize the text parser."""
        self.supported_extensions = ['.txt', '.md', '.rst']
        
    def parse(self, file_path: str) -> Dict[str, Any]:
        """Parse a text document.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Dictionary containing parsed document content
        """
        logger.info(f"Parsing text document: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract title from filename or first line
            title = os.path.basename(file_path).replace('.txt', '')
            lines = content.split('\n')
            if lines and lines[0].strip():
                title = lines[0].strip()
                
            return {
                'title': title,
                'authors': ['Unknown Author'],
                'date': 'Unknown Date',
                'content': content,
                'sections': {}
            }
            
        except Exception as e:
            logger.error(f"Error parsing text document: {e}")
            return {
                'title': os.path.basename(file_path),
                'content': '',
                'error': str(e)
            }


class DocumentParser:
    """Parser for medical documents from various sources."""
    
    def __init__(self):
        """Initialize the document parser."""
        self.pdf_parser = PDFParser()
        self.text_parser = TextParser()
        
    def parse_document(self, source: str) -> Dict[str, Any]:
        """Parse a document from various sources.
        
        Args:
            source: Document source (file path, URL, or PubMed ID)
            
        Returns:
            Dictionary containing parsed document content
        """
        # Check if source is a PubMed ID
        if re.match(r'^\d+$', source):
            return self.parse_pubmed(source)
            
        # Check if source is a URL
        if source.startswith(('http://', 'https://')):
            return self.parse_url(source)
            
        # Check if source is a file path
        if os.path.isfile(source):
            return self.parse_file(source)
            
        # Unknown source
        logger.error(f"Unknown document source: {source}")
        return {
            'title': 'Unknown',
            'authors': [],
            'abstract': '',
            'content': '',
            'sections': {},
            'references': [],
            'source': source,
            'error': 'Unknown document source'
        }
    
    def parse_pubmed(self, pmid: str) -> Dict[str, Any]:
        """Parse a PubMed article.
        
        Args:
            pmid: PubMed ID
            
        Returns:
            Dictionary containing parsed article content
        """
        logger.info(f"Parsing PubMed article with ID: {pmid}")
        
        try:
            # In a real implementation, this would use the PubMed API
            # For demonstration purposes, we'll return a placeholder
            
            # Construct the URL for the PubMed API
            url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"
            
            # Make the request
            response = requests.get(url)
            response.raise_for_status()
            
            # Parse the XML response
            root = ET.fromstring(response.text)
            
            # Extract article information
            article = root.find('.//Article')
            
            if article is None:
                logger.error(f"No article found for PubMed ID: {pmid}")
                return {
                    'title': 'Unknown',
                    'authors': [],
                    'abstract': '',
                    'content': '',
                    'sections': {},
                    'references': [],
                    'source': f"PubMed:{pmid}",
                    'error': 'Article not found'
                }
                
            # Extract title
            title_elem = article.find('./ArticleTitle')
            title = title_elem.text if title_elem is not None else 'Unknown'
            
            # Extract authors
            authors = []
            author_list = article.find('./AuthorList')
            
            if author_list is not None:
                for author_elem in author_list.findall('./Author'):
                    last_name = author_elem.find('./LastName')
                    fore_name = author_elem.find('./ForeName')
                    
                    last = last_name.text if last_name is not None else ''
                    fore = fore_name.text if fore_name is not None else ''
                    
                    if last or fore:
                        authors.append(f"{fore} {last}".strip())
            
            # Extract abstract
            abstract_elem = article.find('.//Abstract')
            abstract = ''
            
            if abstract_elem is not None:
                abstract_texts = abstract_elem.findall('./AbstractText')
                abstract_parts = []
                
                for abstract_text in abstract_texts:
                    label = abstract_text.get('Label', '')
                    text = abstract_text.text or ''
                    
                    if label:
                        abstract_parts.append(f"{label}: {text}")
                    else:
                        abstract_parts.append(text)
                        
                abstract = '\n\n'.join(abstract_parts)
            
            # Extract publication date
            pub_date = article.find('.//PubDate')
            year = pub_date.find('./Year')
            month = pub_date.find('./Month')
            day = pub_date.find('./Day')
            
            date_str = ''
            if year is not None:
                date_str = year.text
                if month is not None:
                    date_str = f"{month.text} {date_str}"
                    if day is not None:
                        date_str = f"{day.text} {date_str}"
            
            # Extract journal information
            journal = article.find('.//Journal')
            journal_title = 'Unknown'
            
            if journal is not None:
                journal_title_elem = journal.find('./Title')
                if journal_title_elem is not None:
                    journal_title = journal_title_elem.text
            
            # Return parsed article
            return {
                'title': title,
                'authors': authors,
                'abstract': abstract,
                'content': abstract,  # Full text not available through basic PubMed API
                'sections': {'abstract': abstract},
                'references': [],
                'source': f"PubMed:{pmid}",
                'journal': journal_title,
                'publication_date': date_str,
                'pmid': pmid
            }
            
        except Exception as e:
            logger.error(f"Error parsing PubMed article: {e}")
            return {
                'title': 'Unknown',
                'authors': [],
                'abstract': '',
                'content': '',
                'sections': {},
                'references': [],
                'source': f"PubMed:{pmid}",
                'error': str(e)
            }
    
    def parse_url(self, url: str) -> Dict[str, Any]:
        """Parse a document from a URL.
        
        Args:
            url: Document URL
            
        Returns:
            Dictionary containing parsed document content
        """
        logger.info(f"Parsing document from URL: {url}")
        
        try:
            # Check if URL is from PubMed
            if 'ncbi.nlm.nih.gov/pubmed' in url or 'pubmed.ncbi.nlm.nih.gov' in url:
                # Extract PubMed ID from URL
                pmid_match = re.search(r'/(\d+)/?$', url)
                
                if pmid_match:
                    pmid = pmid_match.group(1)
                    return self.parse_pubmed(pmid)
            
            # For other URLs, make a request and parse the content
            response = requests.get(url)
            response.raise_for_status()
            
            # In a real implementation, this would use a more sophisticated HTML parser
            # For demonstration purposes, we'll return a placeholder
            
            return {
                'title': 'Web Document',
                'authors': [],
                'abstract': '',
                'content': response.text[:1000] + '...',  # Truncate content for demonstration
                'sections': {},
                'references': [],
                'source': url
            }
            
        except Exception as e:
            logger.error(f"Error parsing document from URL: {e}")
            return {
                'title': 'Unknown',
                'authors': [],
                'abstract': '',
                'content': '',
                'sections': {},
                'references': [],
                'source': url,
                'error': str(e)
            }
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse a document from a file.
        
        Args:
            file_path: Path to document file
            
        Returns:
            Dictionary containing parsed document content
        """
        logger.info(f"Parsing document from file: {file_path}")
        
        try:
            # Get file extension
            _, ext = os.path.splitext(file_path)
            ext = ext.lower()
            
            # Parse based on file type
            if ext == '.pdf':
                return self.parse_pdf(file_path)
            elif ext in ['.txt', '.text']:
                return self.parse_text(file_path)
            elif ext in ['.xml', '.html', '.htm']:
                return self.parse_xml_html(file_path)
            else:
                logger.error(f"Unsupported file type: {ext}")
                return {
                    'title': os.path.basename(file_path),
                    'authors': [],
                    'abstract': '',
                    'content': '',
                    'sections': {},
                    'references': [],
                    'source': file_path,
                    'error': f"Unsupported file type: {ext}"
                }
                
        except Exception as e:
            logger.error(f"Error parsing document from file: {e}")
            return {
                'title': os.path.basename(file_path),
                'authors': [],
                'abstract': '',
                'content': '',
                'sections': {},
                'references': [],
                'source': file_path,
                'error': str(e)
            }
    
    def parse_pdf(self, file_path: str) -> Dict[str, Any]:
        """Parse a PDF document.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary containing parsed document content
        """
        logger.info(f"Parsing PDF document: {file_path}")
        
        try:
            # In a real implementation, this would use a PDF parser like PyPDF2 or pdfminer
            # For demonstration purposes, we'll return a placeholder
            
            return {
                'title': os.path.basename(file_path),
                'authors': [],
                'abstract': 'PDF abstract extraction not implemented',
                'content': 'PDF content extraction not implemented',
                'sections': {},
                'references': [],
                'source': file_path
            }
            
        except Exception as e:
            logger.error(f"Error parsing PDF document: {e}")
            return {
                'title': os.path.basename(file_path),
                'authors': [],
                'abstract': '',
                'content': '',
                'sections': {},
                'references': [],
                'source': file_path,
                'error': str(e)
            }
    
    def parse_text(self, file_path: str) -> Dict[str, Any]:
        """Parse a plain text document.
        
        Args:
            file_path: Path to text file
            
        Returns:
            Dictionary containing parsed document content
        """
        logger.info(f"Parsing text document: {file_path}")
        
        try:
            # Read the text file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract title (first line)
            lines = content.split('\n')
            title = lines[0] if lines else os.path.basename(file_path)
            
            # Extract abstract (look for "Abstract" section)
            abstract = ''
            abstract_match = re.search(r'(?:Abstract|ABSTRACT)[:\s]*(.*?)(?:\n\n|\n[A-Z][A-Z\s]+:)', content, re.DOTALL)
            
            if abstract_match:
                abstract = abstract_match.group(1).strip()
                
            # Extract sections
            sections = {}
            section_pattern = re.compile(r'\n([A-Z][A-Z\s]+):\s*(.*?)(?=\n[A-Z][A-Z\s]+:|\Z)', re.DOTALL)
            
            for match in section_pattern.finditer(content):
                section_name = match.group(1).strip().lower()
                section_content = match.group(2).strip()
                sections[section_name] = section_content
                
            # Return parsed document
            return {
                'title': title,
                'authors': [],
                'abstract': abstract,
                'content': content,
                'sections': sections,
                'references': [],
                'source': file_path
            }
            
        except Exception as e:
            logger.error(f"Error parsing text document: {e}")
            return {
                'title': os.path.basename(file_path),
                'authors': [],
                'abstract': '',
                'content': '',
                'sections': {},
                'references': [],
                'source': file_path,
                'error': str(e)
            }
    
    def parse_xml_html(self, file_path: str) -> Dict[str, Any]:
        """Parse an XML or HTML document.
        
        Args:
            file_path: Path to XML or HTML file
            
        Returns:
            Dictionary containing parsed document content
        """
        logger.info(f"Parsing XML/HTML document: {file_path}")
        
        try:
            # In a real implementation, this would use a proper XML/HTML parser
            # For demonstration purposes, we'll return a placeholder
            
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            return {
                'title': os.path.basename(file_path),
                'authors': [],
                'abstract': 'XML/HTML abstract extraction not implemented',
                'content': content[:1000] + '...',  # Truncate content for demonstration
                'sections': {},
                'references': [],
                'source': file_path
            }
            
        except Exception as e:
            logger.error(f"Error parsing XML/HTML document: {e}")
            return {
                'title': os.path.basename(file_path),
                'authors': [],
                'abstract': '',
                'content': '',
                'sections': {},
                'references': [],
                'source': file_path,
                'error': str(e)
            }
    
    def extract_sections(self, content: str) -> Dict[str, str]:
        """Extract sections from document content.
        
        Args:
            content: Document content
            
        Returns:
            Dictionary mapping section names to section content
        """
        # Look for common section headers in medical papers
        section_headers = [
            'abstract', 'introduction', 'background', 'methods', 'methodology',
            'results', 'discussion', 'conclusion', 'conclusions', 'references'
        ]
        
        sections = {}
        
        # Create pattern to match section headers
        pattern = r'\n(' + '|'.join(section_headers) + r')[\s:]+(.+?)(?=\n(?:' + '|'.join(section_headers) + r')[\s:]|\Z)'
        matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            section_name = match.group(1).lower()
            section_content = match.group(2).strip()
            sections[section_name] = section_content
            
        return sections
