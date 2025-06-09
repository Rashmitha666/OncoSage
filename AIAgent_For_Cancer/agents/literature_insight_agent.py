"""
Literature Insight Agent
Function: Reads medical papers and extracts key takeaways.
"""
import os
import json
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

from utils.api_clients import PubMedClient
from utils.nlp_processor import NLPProcessor
from utils.document_parser import PDFParser, TextParser

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LiteratureInsightAgent:
    """Agent that analyzes medical literature and extracts key insights."""
    
    def __init__(self, config_path: str = None):
        """Initialize the literature insight agent.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.pubmed_client = PubMedClient(self.config.get('pubmed_api_key', ''))
        self.nlp_processor = NLPProcessor()
        self.pdf_parser = PDFParser()
        self.text_parser = TextParser()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file."""
        if not config_path:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                      'config', 'literature_insight_config.json')
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found at {config_path}. Using default configuration.")
            return {
                'pubmed_api_key': '',
                'max_papers': 10,
                'extract_sections': ['abstract', 'introduction', 'methods', 'results', 'discussion', 'conclusion'],
                'summary_length': 300,  # words
                'highlight_keywords': ['significant', 'novel', 'improvement', 'survival', 'efficacy'],
                'insight_categories': ['clinical_implications', 'research_directions', 'treatment_approaches']
            }
    
    def analyze_paper(self, paper_id: str = None, paper_url: str = None, 
                     paper_path: str = None) -> Dict[str, Any]:
        """Analyze a single medical paper and extract insights.
        
        Args:
            paper_id: PubMed ID of the paper
            paper_url: URL to the paper
            paper_path: Local path to the paper file
            
        Returns:
            Dictionary containing paper analysis and insights
        """
        # Get paper content
        if paper_id:
            paper_content = self.pubmed_client.get_paper_content(paper_id)
            paper_metadata = self.pubmed_client.get_paper_metadata(paper_id)
        elif paper_url:
            if paper_url.endswith('.pdf'):
                paper_content = self.pdf_parser.parse_from_url(paper_url)
            else:
                paper_content = self.text_parser.parse_from_url(paper_url)
            paper_metadata = self._extract_metadata_from_content(paper_content)
        elif paper_path:
            if paper_path.endswith('.pdf'):
                paper_content = self.pdf_parser.parse_from_file(paper_path)
            else:
                paper_content = self.text_parser.parse_from_file(paper_path)
            paper_metadata = self._extract_metadata_from_content(paper_content)
        else:
            raise ValueError("Must provide either paper_id, paper_url, or paper_path")
        
        # Extract sections
        sections = self._extract_sections(paper_content)
        
        # Generate summary
        summary = self._generate_summary(sections)
        
        # Extract key findings
        key_findings = self._extract_key_findings(sections)
        
        # Extract clinical implications
        clinical_implications = self._extract_clinical_implications(sections)
        
        # Generate insights
        insights = self._generate_insights(sections, paper_metadata)
        
        return {
            'metadata': paper_metadata,
            'summary': summary,
            'key_findings': key_findings,
            'clinical_implications': clinical_implications,
            'insights': insights,
            'analyzed_at': datetime.now().isoformat()
        }
    
    def analyze_papers(self, query: str, max_papers: int = None) -> List[Dict[str, Any]]:
        """Search for papers matching a query and analyze them.
        
        Args:
            query: Search query
            max_papers: Maximum number of papers to analyze
            
        Returns:
            List of paper analyses
        """
        if not max_papers:
            max_papers = self.config.get('max_papers', 10)
            
        # Search for papers
        papers = self.pubmed_client.search(query, max_results=max_papers)
        
        # Analyze each paper
        analyses = []
        for paper in papers:
            try:
                analysis = self.analyze_paper(paper_id=paper['id'])
                analyses.append(analysis)
            except Exception as e:
                logger.error(f"Error analyzing paper {paper['id']}: {e}")
                
        return analyses
    
    def _extract_metadata_from_content(self, content: str) -> Dict[str, Any]:
        """Extract metadata from paper content."""
        # This is a simplified implementation
        metadata = {
            'title': '',
            'authors': [],
            'journal': '',
            'publication_date': '',
            'doi': ''
        }
        
        # Try to extract title
        title_match = re.search(r'^(.*?)\n', content)
        if title_match:
            metadata['title'] = title_match.group(1).strip()
            
        # Try to extract authors
        authors_match = re.search(r'\n(.*?)\n.*?Abstract', content, re.DOTALL)
        if authors_match:
            authors_text = authors_match.group(1)
            # Simple splitting by commas and 'and'
            authors = re.split(r',|\sand\s', authors_text)
            metadata['authors'] = [author.strip() for author in authors if author.strip()]
            
        # Try to extract DOI
        doi_match = re.search(r'doi:?\s*(10\.\d+/[^\s]+)', content, re.IGNORECASE)
        if doi_match:
            metadata['doi'] = doi_match.group(1)
            
        return metadata
    
    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract sections from paper content."""
        sections = {}
        
        # Define common section headers in medical papers
        section_patterns = {
            'abstract': r'Abstract\s*\n(.*?)(?:\n\s*Introduction|\n\s*Background|\Z)',
            'introduction': r'Introduction\s*\n(.*?)(?:\n\s*Methods|\n\s*Materials and Methods|\Z)',
            'methods': r'(?:Methods|Materials and Methods)\s*\n(.*?)(?:\n\s*Results|\Z)',
            'results': r'Results\s*\n(.*?)(?:\n\s*Discussion|\Z)',
            'discussion': r'Discussion\s*\n(.*?)(?:\n\s*Conclusion|\Z)',
            'conclusion': r'Conclusion\s*\n(.*?)(?:\n\s*References|\Z)'
        }
        
        # Extract each section using regex
        for section_name, pattern in section_patterns.items():
            if section_name in self.config.get('extract_sections', []):
                match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                if match:
                    sections[section_name] = match.group(1).strip()
                else:
                    sections[section_name] = ""
                    
        return sections
    
    def _generate_summary(self, sections: Dict[str, str]) -> str:
        """Generate a summary of the paper."""
        # Combine relevant sections
        text_to_summarize = ""
        for section in ['abstract', 'conclusion']:
            if section in sections and sections[section]:
                text_to_summarize += sections[section] + " "
                
        # Use NLP processor to generate summary
        summary_length = self.config.get('summary_length', 300)
        summary = self.nlp_processor.generate_summary(text_to_summarize, max_length=summary_length)
        
        return summary
    
    def _extract_key_findings(self, sections: Dict[str, str]) -> List[str]:
        """Extract key findings from the paper."""
        # Focus on results and discussion sections
        text_to_analyze = ""
        for section in ['results', 'discussion']:
            if section in sections and sections[section]:
                text_to_analyze += sections[section] + " "
                
        # Use NLP processor to extract key findings
        findings = self.nlp_processor.extract_key_points(
            text_to_analyze, 
            keywords=self.config.get('highlight_keywords', [])
        )
        
        return findings
    
    def _extract_clinical_implications(self, sections: Dict[str, str]) -> List[str]:
        """Extract clinical implications from the paper."""
        # Focus on discussion and conclusion sections
        text_to_analyze = ""
        for section in ['discussion', 'conclusion']:
            if section in sections and sections[section]:
                text_to_analyze += sections[section] + " "
                
        # Use NLP processor to extract clinical implications
        implications = self.nlp_processor.extract_clinical_implications(text_to_analyze)
        
        return implications
    
    def _generate_insights(self, sections: Dict[str, str], metadata: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate insights from the paper."""
        insights = {}
        
        # Generate insights for each configured category
        for category in self.config.get('insight_categories', []):
            if category == 'clinical_implications':
                insights[category] = self._extract_clinical_implications(sections)
            elif category == 'research_directions':
                insights[category] = self._extract_research_directions(sections)
            elif category == 'treatment_approaches':
                insights[category] = self._extract_treatment_approaches(sections)
                
        return insights
    
    def _extract_research_directions(self, sections: Dict[str, str]) -> List[str]:
        """Extract future research directions from the paper."""
        # Focus on discussion and conclusion sections
        text_to_analyze = ""
        for section in ['discussion', 'conclusion']:
            if section in sections and sections[section]:
                text_to_analyze += sections[section] + " "
                
        # Use NLP processor to extract research directions
        directions = self.nlp_processor.extract_research_directions(text_to_analyze)
        
        return directions
    
    def _extract_treatment_approaches(self, sections: Dict[str, str]) -> List[str]:
        """Extract treatment approaches from the paper."""
        # Analyze all sections
        text_to_analyze = " ".join([section for section in sections.values() if section])
                
        # Use NLP processor to extract treatment approaches
        approaches = self.nlp_processor.extract_treatment_approaches(text_to_analyze)
        
        return approaches

if __name__ == "__main__":
    # For testing purposes
    agent = LiteratureInsightAgent()
    
    # Test with a PubMed ID
    paper_id = "33085857"  # Example PubMed ID for a lung cancer paper
    analysis = agent.analyze_paper(paper_id=paper_id)
    
    print(f"Paper: {analysis['metadata']['title']}")
    print(f"Summary: {analysis['summary']}")
    print(f"Key findings: {analysis['key_findings']}")
    print(f"Clinical implications: {analysis['clinical_implications']}")
