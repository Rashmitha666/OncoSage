"""
Oncology AI Assistant System
Main application that integrates all the AI agents for oncology assistance.
"""
import os
import sys
import logging
import argparse
from datetime import datetime
import json
from typing import Dict, List, Any

# Import agents
from agents.news_research_agent import NewsResearchAgent
from agents.clinical_trials_agent import ClinicalTrialsAgent
from agents.literature_insight_agent import LiteratureInsightAgent
from agents.twitter_trends_agent import TwitterTrendsAgent
from agents.drug_safety_agent import DrugSafetyAgent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("oncology_assistant.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class OncologyAssistantSystem:
    """Main system that integrates all oncology AI agents."""
    
    def __init__(self, config_path: str = None):
        """Initialize the oncology assistant system.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        
        # Initialize agents
        logger.info("Initializing oncology AI agents")
        self.news_agent = NewsResearchAgent()
        self.trials_agent = ClinicalTrialsAgent()
        self.literature_agent = LiteratureInsightAgent()
        self.twitter_agent = TwitterTrendsAgent()
        self.drug_safety_agent = DrugSafetyAgent()
        
        # Initialize voice assistant if configured
        self.voice_assistant = None
        if self.config.get('enable_voice_assistant', False):
            try:
                from agents.voice_assistant_agent import VoiceAssistantAgent
                self.voice_assistant = VoiceAssistantAgent()
                logger.info("Voice assistant initialized successfully")
            except ImportError:
                logger.warning("Voice assistant module not found or could not be initialized")
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file."""
        if not config_path:
            config_path = os.path.join(os.path.dirname(__file__), 'config', 'system_config.json')
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found at {config_path}. Using default configuration.")
            return {
                'enable_voice_assistant': False,
                'update_frequency_hours': 24,
                'notification_methods': ['dashboard', 'email'],
                'notification_recipients': [],
                'web_dashboard_port': 8050
            }
    
    def run_all_agents(self) -> Dict[str, Any]:
        """Run all agents and collect their results."""
        logger.info("Running all oncology AI agents")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'news_research': None,
            'clinical_trials': None,
            'literature_insights': None,
            'twitter_trends': None,
            'drug_safety': None
        }
        
        # Run news research agent
        try:
            logger.info("Running news research agent")
            results['news_research'] = self.news_agent.generate_update()
        except Exception as e:
            logger.error(f"Error running news research agent: {e}")
            
        # Run clinical trials agent (requires patient profile)
        # This would typically be run on demand with a specific patient profile
        
        # Run literature insight agent (requires specific papers)
        # This would typically be run on demand with specific papers
        
        # Run Twitter trends agent
        try:
            logger.info("Running Twitter trends agent")
            results['twitter_trends'] = self.twitter_agent.generate_trends_report()
        except Exception as e:
            logger.error(f"Error running Twitter trends agent: {e}")
            
        # Run drug safety agent
        try:
            logger.info("Running drug safety agent")
            results['drug_safety'] = self.drug_safety_agent.run_safety_check()
        except Exception as e:
            logger.error(f"Error running drug safety agent: {e}")
            
        return results
    
    def start_web_dashboard(self) -> None:
        """Start the web dashboard for the oncology assistant system."""
        try:
            from web.dashboard import start_dashboard
            port = self.config.get('web_dashboard_port', 8050)
            logger.info(f"Starting web dashboard on port {port}")
            start_dashboard(self, port=port)
        except ImportError:
            logger.error("Web dashboard module not found or could not be initialized")
            
    def start_voice_assistant(self) -> None:
        """Start the voice assistant for the oncology assistant system."""
        if self.voice_assistant:
            logger.info("Starting voice assistant")
            self.voice_assistant.start()
        else:
            logger.warning("Voice assistant not initialized")
            
    def run(self, start_dashboard: bool = True, start_voice: bool = False) -> None:
        """Run the oncology assistant system."""
        # Run all agents
        results = self.run_all_agents()
        
        # Save results
        output_dir = os.path.join(os.path.dirname(__file__), 'data', 'results')
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(output_dir, f'results_{timestamp}.json')
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
            
        logger.info(f"Results saved to {output_path}")
        
        # Start web dashboard if requested
        if start_dashboard:
            self.start_web_dashboard()
            
        # Start voice assistant if requested
        if start_voice and self.voice_assistant:
            self.start_voice_assistant()

def main():
    """Main entry point for the oncology assistant system."""
    parser = argparse.ArgumentParser(description='Oncology AI Assistant System')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--no-dashboard', action='store_true', help='Do not start the web dashboard')
    parser.add_argument('--voice', action='store_true', help='Start the voice assistant')
    
    args = parser.parse_args()
    
    system = OncologyAssistantSystem(config_path=args.config)
    system.run(start_dashboard=not args.no_dashboard, start_voice=args.voice)

if __name__ == "__main__":
    main()
    
