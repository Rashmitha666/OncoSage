"""
Demo script for the Oncology AI Assistant System.
This script demonstrates the functionality of the various components.
"""
import os
import logging
import sys
from datetime import datetime
from utils.config_loader import ConfigLoader
from utils.pubmed_client import PubMedClient
from utils.clinical_trials_client import ClinicalTrialsClient
from utils.twitter_client import TwitterClient
from utils.fda_client import FDAClient
from utils.nlp_processor import NLPProcessor
from utils.document_parser import DocumentParser
from utils.patient_profile import PatientProfile, Location
from utils.notification import NotificationService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Run the demo."""
    logger.info("Starting Oncology AI Assistant System Demo")
    
    # Load configuration
    config_loader = ConfigLoader()
    system_config = config_loader.get_system_config()
    logger.info(f"Loaded system configuration: {system_config}")
    
    # Initialize API clients
    pubmed_client = PubMedClient(api_key=config_loader.get_api_key("pubmed"))
    clinical_trials_client = ClinicalTrialsClient()
    twitter_client = TwitterClient(
        consumer_key=config_loader.get_api_key("twitter_consumer_key"),
        consumer_secret=config_loader.get_api_key("twitter_consumer_secret"),
        access_token=config_loader.get_api_key("twitter_access_token"),
        access_token_secret=config_loader.get_api_key("twitter_access_token_secret")
    )
    fda_client = FDAClient(api_key=config_loader.get_api_key("fda"))
    
    # Initialize utilities
    nlp_processor = NLPProcessor()
    document_parser = DocumentParser()
    # Get config path for notification service
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'default_config.json')
    notification_service = NotificationService(config_path)
    
    # Demo: Search PubMed for lung cancer research
    logger.info("Searching PubMed for lung cancer research...")
    search_results = pubmed_client.search(
        query="lung cancer EGFR mutation",
        max_results=5
    )
    logger.info(f"Found {len(search_results)} articles")
    
    if search_results:
        # Get details for first article
        article_id = search_results[0].get("id")
        logger.info(f"Getting details for article {article_id}")
        article = pubmed_client.get_article(article_id)
        
        # Process article with NLP
        if article and article.get("abstract"):
            logger.info("Processing article with NLP...")
            keywords = nlp_processor.extract_keywords(article.get("abstract"))
            summary = nlp_processor.summarize_text(article.get("abstract"))
            
            logger.info(f"Keywords: {keywords}")
            logger.info(f"Summary: {summary}")
    
    # Demo: Search for clinical trials
    logger.info("Searching for lung cancer clinical trials...")
    trials = clinical_trials_client.search_lung_cancer_trials(
        biomarkers=["EGFR"],
        recruiting_only=True,
        max_results=5
    )
    logger.info(f"Found {len(trials)} clinical trials")
    
    # Demo: Create a patient profile
    logger.info("Creating patient profile...")
    patient = PatientProfile(
        patient_id="P12345",
        age=65,
        gender="Female",
        cancer_type="Non-small cell lung cancer",
        cancer_stage="IV",
        biomarkers={"EGFR": "positive"},
        prior_treatments=["Osimertinib"],
        performance_status=1,
        location=Location(
            city="New York",
            state="NY"
        )
    )
    logger.info(f"Patient profile created: {patient.to_dict()}")
    
    # Demo: Search Twitter for lung cancer updates
    logger.info("Searching Twitter for lung cancer updates...")
    tweets = twitter_client.search_tweets(
        query="lung cancer EGFR",
        max_results=5
    )
    logger.info(f"Found {len(tweets)} tweets")
    
    # Demo: Check FDA for drug safety information
    logger.info("Checking FDA for drug safety information...")
    safety_info = fda_client.search_drug_events(
        drug_name="osimertinib",
        limit=5
    )
    logger.info(f"Found {len(safety_info)} safety reports")
    
    # Demo: Send notification
    logger.info("Sending notification...")
    notification_service.send_dashboard_alert(
        "research_update",
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "articles": [article] if article else [],
            "trials": trials,
            "tweets": tweets,
            "safety_reports": safety_info
        }
    )
    
    logger.info("Demo completed successfully!")

if __name__ == "__main__":
    main()
