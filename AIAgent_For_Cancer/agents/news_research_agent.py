"""
Clinical News & Research Update Agent
Function: Keeps oncologists updated with the latest lung cancer research, trials, and therapies.
"""
import os
import requests
from datetime import datetime, timedelta
import json
from typing import List, Dict, Any
import logging

from utils.api_clients import PubMedClient, ClinicalTrialsClient
from utils.notification import NotificationService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NewsResearchAgent:
    """Agent that fetches and processes the latest lung cancer research and news."""
    
    def __init__(self, config_path: str = None):
        """Initialize the news research agent.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.pubmed_client = PubMedClient(self.config.get('pubmed_api_key', ''))
        self.clinical_trials_client = ClinicalTrialsClient()
        self.notification_service = NotificationService()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file."""
        if not config_path:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                      'config', 'news_research_config.json')
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found at {config_path}. Using default configuration.")
            return {
                'update_frequency': 24,  # hours
                'search_terms': ['lung cancer', 'NSCLC', 'SCLC', 'lung adenocarcinoma', 
                                'lung squamous cell carcinoma', 'immunotherapy lung cancer'],
                'max_results': 50,
                'days_lookback': 7
            }
    
    def get_latest_research(self) -> List[Dict[str, Any]]:
        """Fetch the latest research papers on lung cancer."""
        results = []
        
        for term in self.config.get('search_terms', []):
            logger.info(f"Searching PubMed for term: {term}")
            papers = self.pubmed_client.search(
                term, 
                max_results=self.config.get('max_results', 50),
                days_lookback=self.config.get('days_lookback', 7)
            )
            results.extend(papers)
            
        # Remove duplicates based on paper ID
        unique_results = {paper['id']: paper for paper in results}.values()
        
        # Sort by date (newest first)
        sorted_results = sorted(unique_results, key=lambda x: x.get('publication_date', ''), reverse=True)
        
        return list(sorted_results)
    
    def get_latest_trials(self) -> List[Dict[str, Any]]:
        """Fetch the latest clinical trials for lung cancer."""
        trials = self.clinical_trials_client.search(
            condition='lung cancer',
            status='recruiting',
            max_results=self.config.get('max_results', 50)
        )
        
        # Sort by last updated date
        sorted_trials = sorted(trials, key=lambda x: x.get('last_updated', ''), reverse=True)
        
        return sorted_trials
    
    def get_latest_therapies(self) -> List[Dict[str, Any]]:
        """Fetch information about the latest therapies for lung cancer."""
        # This could come from multiple sources: FDA approvals, clinical trials, research papers
        therapies = []
        
        # Get FDA approvals (this would be implemented in a real API client)
        # therapies.extend(self.fda_client.get_recent_approvals('lung cancer'))
        
        # Extract therapy information from clinical trials
        trials = self.get_latest_trials()
        for trial in trials:
            if 'intervention' in trial:
                therapies.append({
                    'name': trial['intervention'].get('name', 'Unknown'),
                    'type': trial['intervention'].get('type', 'Unknown'),
                    'description': trial.get('brief_summary', ''),
                    'source': f"Clinical Trial: {trial.get('id')}",
                    'date': trial.get('last_updated')
                })
        
        # Remove duplicates and sort by date
        unique_therapies = {therapy['name']: therapy for therapy in therapies}.values()
        sorted_therapies = sorted(unique_therapies, key=lambda x: x.get('date', ''), reverse=True)
        
        return list(sorted_therapies)
    
    def generate_update(self) -> Dict[str, Any]:
        """Generate a comprehensive update on lung cancer research, trials, and therapies."""
        update = {
            'timestamp': datetime.now().isoformat(),
            'research': self.get_latest_research(),
            'clinical_trials': self.get_latest_trials(),
            'therapies': self.get_latest_therapies()
        }
        
        return update
    
    def send_update(self, recipients: List[str] = None) -> bool:
        """Generate and send an update to specified recipients."""
        update = self.generate_update()
        
        if not recipients:
            recipients = self.config.get('default_recipients', [])
        
        return self.notification_service.send_update(update, recipients)
    
    def run_scheduled_update(self) -> None:
        """Run a scheduled update based on configuration."""
        logger.info("Running scheduled update for lung cancer research and news")
        self.send_update()

if __name__ == "__main__":
    # For testing purposes
    agent = NewsResearchAgent()
    update = agent.generate_update()
    print(f"Found {len(update['research'])} research papers")
    print(f"Found {len(update['clinical_trials'])} clinical trials")
    print(f"Found {len(update['therapies'])} therapies")
