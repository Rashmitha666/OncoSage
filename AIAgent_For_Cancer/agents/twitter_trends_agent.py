"""
Twitter/X Research Trends Monitor Agent
Function: Scans verified medical accounts (oncologists, pharma companies) for breaking news on lung cancer.
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import re

from utils.api_clients import TwitterClient
from utils.nlp_processor import NLPProcessor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TwitterTrendsAgent:
    """Agent that monitors Twitter/X for lung cancer research trends."""
    
    def __init__(self, config_path: str = None):
        """Initialize the Twitter/X trends monitoring agent.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.twitter_client = TwitterClient(
            consumer_key=self.config.get('twitter_consumer_key', ''),
            consumer_secret=self.config.get('twitter_consumer_secret', ''),
            access_token=self.config.get('twitter_access_token', ''),
            access_token_secret=self.config.get('twitter_access_token_secret', '')
        )
        self.nlp_processor = NLPProcessor()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file."""
        if not config_path:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                      'config', 'twitter_trends_config.json')
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found at {config_path}. Using default configuration.")
            return {
                'twitter_api_key': '',
                'twitter_api_secret': '',
                'twitter_access_token': '',
                'twitter_access_token_secret': '',
                'verified_accounts': [
                    'ASCO', 'theNCI', 'IASLC', 'AmerMedicalAssn', 'NEJM', 'JAMA_current',
                    'LUNGevity', 'GO2Foundation', 'LungCancerFaces', 'AstraZeneca', 'Pfizer',
                    'Roche', 'MerckUS', 'BristolMyersSquibb', 'JanssenGlobal'
                ],
                'oncologist_list_id': '',  # Twitter list ID containing oncologists
                'search_terms': [
                    'lung cancer', 'NSCLC', 'SCLC', 'lung adenocarcinoma', 'lung squamous cell carcinoma',
                    'EGFR', 'ALK', 'ROS1', 'BRAF', 'MET', 'RET', 'NTRK', 'PD-L1', 'PD-1',
                    'immunotherapy lung', 'targeted therapy lung', 'lung cancer trial'
                ],
                'days_lookback': 7,
                'min_retweets': 5,
                'min_likes': 10,
                'include_replies': False,
                'include_retweets': True
            }
    
    def monitor_verified_accounts(self) -> List[Dict[str, Any]]:
        """Monitor tweets from verified medical accounts."""
        tweets = []
        
        # Get tweets from verified accounts
        for account in self.config.get('verified_accounts', []):
            logger.info(f"Fetching tweets from account: {account}")
            account_tweets = self.twitter_client.get_user_tweets(
                username=account,
                days_lookback=self.config.get('days_lookback', 7),
                max_results=self.config.get('max_results', 50)
            )
            
            # Filter tweets related to lung cancer
            filtered_tweets = self._filter_lung_cancer_tweets(account_tweets)
            tweets.extend(filtered_tweets)
            
        # Get tweets from oncologist list if configured
        oncologist_list_id = self.config.get('oncologist_list_id')
        if oncologist_list_id:
            logger.info(f"Fetching tweets from oncologist list: {oncologist_list_id}")
            list_tweets = self.twitter_client.get_list_tweets(
                list_id=oncologist_list_id,
                days_lookback=self.config.get('days_lookback', 7)
            )
            
            # Filter tweets related to lung cancer
            filtered_tweets = self._filter_lung_cancer_tweets(list_tweets)
            tweets.extend(filtered_tweets)
            
        # Filter by engagement metrics
        min_retweets = self.config.get('min_retweets', 5)
        min_likes = self.config.get('min_likes', 10)
        
        engagement_filtered_tweets = [
            tweet for tweet in tweets 
            if tweet.get('retweet_count', 0) >= min_retweets and 
               tweet.get('like_count', 0) >= min_likes
        ]
        
        # Sort by engagement (retweets + likes)
        sorted_tweets = sorted(
            engagement_filtered_tweets,
            key=lambda x: (x.get('retweet_count', 0) + x.get('like_count', 0)),
            reverse=True
        )
        
        return sorted_tweets
    
    def search_lung_cancer_trends(self) -> List[Dict[str, Any]]:
        """Search for lung cancer trends across Twitter/X."""
        all_tweets = []
        
        # Search for each term
        for term in self.config.get('search_terms', []):
            logger.info(f"Searching Twitter for term: {term}")
            term_tweets = self.twitter_client.search_tweets(
                query=term,
                days=self.config.get('days_lookback', 7)
            )
            all_tweets.extend(term_tweets)
            
        # Filter by engagement metrics
        min_retweets = self.config.get('min_retweets', 5)
        min_likes = self.config.get('min_likes', 10)
        
        engagement_filtered_tweets = [
            tweet for tweet in all_tweets 
            if tweet.get('retweet_count', 0) >= min_retweets and 
               tweet.get('like_count', 0) >= min_likes
        ]
        
        # Filter for verified accounts only
        verified_tweets = [
            tweet for tweet in engagement_filtered_tweets
            if tweet.get('user', {}).get('verified', False)
        ]
        
        # Sort by engagement (retweets + likes)
        sorted_tweets = sorted(
            verified_tweets,
            key=lambda x: (x.get('retweet_count', 0) + x.get('like_count', 0)),
            reverse=True
        )
        
        return sorted_tweets
    
    def _filter_lung_cancer_tweets(self, tweets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter tweets to only include those related to lung cancer."""
        lung_cancer_tweets = []
        
        # Define lung cancer related terms
        lung_cancer_terms = [
            'lung cancer', 'nsclc', 'sclc', 'lung adenocarcinoma', 'lung squamous',
            'egfr', 'alk', 'ros1', 'braf', 'met exon', 'ret fusion', 'ntrk', 'pd-l1', 'pd-1',
            'immunotherapy lung', 'targeted therapy lung', 'lung cancer trial'
        ]
        
        # Create regex pattern for efficient matching
        pattern = re.compile('|'.join(lung_cancer_terms), re.IGNORECASE)
        
        for tweet in tweets:
            text = tweet.get('text', '').lower()
            if pattern.search(text):
                lung_cancer_tweets.append(tweet)
                
        return lung_cancer_tweets
    
    def extract_trending_topics(self, tweets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract trending topics from a collection of tweets."""
        # Extract text from tweets
        texts = [tweet.get('text', '') for tweet in tweets]
        combined_text = ' '.join(texts)
        
        # Use NLP processor to extract topics
        topics = self.nlp_processor.extract_topics(combined_text)
        
        # Count mentions of each topic in tweets
        topic_counts = {}
        for topic in topics:
            topic_lower = topic.lower()
            count = sum(1 for text in texts if topic_lower in text.lower())
            topic_counts[topic] = count
            
        # Convert to list of dictionaries
        trending_topics = [
            {'topic': topic, 'count': count}
            for topic, count in topic_counts.items()
        ]
        
        # Sort by count
        sorted_topics = sorted(trending_topics, key=lambda x: x['count'], reverse=True)
        
        return sorted_topics
    
    def generate_trends_report(self) -> Dict[str, Any]:
        """Generate a comprehensive report on lung cancer trends from Twitter/X."""
        # Get tweets from verified accounts
        verified_tweets = self.monitor_verified_accounts()
        
        # Get tweets from search
        search_tweets = self.search_lung_cancer_trends()
        
        # Combine and deduplicate tweets
        all_tweet_ids = set()
        combined_tweets = []
        
        for tweet in verified_tweets + search_tweets:
            tweet_id = tweet.get('id')
            if tweet_id and tweet_id not in all_tweet_ids:
                all_tweet_ids.add(tweet_id)
                combined_tweets.append(tweet)
                
        # Extract trending topics
        trending_topics = self.extract_trending_topics(combined_tweets)
        
        # Group tweets by topic
        tweets_by_topic = {}
        for topic in [t['topic'] for t in trending_topics]:
            topic_lower = topic.lower()
            tweets_by_topic[topic] = [
                tweet for tweet in combined_tweets
                if topic_lower in tweet.get('text', '').lower()
            ]
            
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'period': f"Past {self.config.get('days_lookback', 7)} days",
            'total_tweets_analyzed': len(combined_tweets),
            'trending_topics': trending_topics,
            'tweets_by_topic': tweets_by_topic,
            'top_tweets': sorted(combined_tweets, 
                               key=lambda x: (x.get('retweet_count', 0) + x.get('like_count', 0)),
                               reverse=True)[:10]
        }
        
        return report

if __name__ == "__main__":
    # For testing purposes
    agent = TwitterTrendsAgent()
    report = agent.generate_trends_report()
    
    print(f"Generated report for {report['period']}")
    print(f"Analyzed {report['total_tweets_analyzed']} tweets")
    print("\nTop trending topics:")
    for topic in report['trending_topics'][:5]:
        print(f"- {topic['topic']}: {topic['count']} mentions")
        
    print("\nTop tweets:")
    for i, tweet in enumerate(report['top_tweets'][:3], 1):
        print(f"{i}. @{tweet['user']['username']}: {tweet['text'][:100]}... " +
              f"({tweet['retweet_count']} RTs, {tweet['like_count']} likes)")
