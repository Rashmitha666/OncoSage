"""
NLP processor for the Oncology AI Assistant System.
Provides text analysis and processing capabilities for medical text.
"""
import re
import logging
from typing import List, Dict, Any, Optional
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download required NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
    
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class NLPProcessor:
    """NLP processor for medical text analysis."""
    
    def __init__(self):
        """Initialize the NLP processor."""
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Add medical stopwords
        self.stop_words.update([
            'patient', 'patients', 'study', 'studies', 'result', 'results',
            'method', 'methods', 'conclusion', 'conclusions', 'background',
            'objective', 'objectives', 'aim', 'aims', 'purpose', 'significance',
            'data', 'analysis', 'analyze', 'measure', 'measures', 'measured',
            'using', 'used', 'use', 'performed', 'conduct', 'conducted',
            'include', 'includes', 'including', 'included', 'exclude', 'excluded',
            'show', 'shows', 'shown', 'indicate', 'indicates', 'indicated',
            'suggest', 'suggests', 'suggested', 'report', 'reports', 'reported'
        ])
        
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis.
        
        Args:
            text: Input text
            
        Returns:
            Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into sentences.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        return sent_tokenize(text)
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Extract keywords from text.
        
        Args:
            text: Input text
            top_n: Number of top keywords to return
            
        Returns:
            List of keywords
        """
        # Preprocess text
        text = self.preprocess_text(text)
        
        # Tokenize into words
        words = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        words = [self.lemmatizer.lemmatize(word) for word in words if word not in self.stop_words]
        
        # Count word frequencies
        word_freq = {}
        for word in words:
            if len(word) > 2:  # Only consider words with more than 2 characters
                word_freq[word] = word_freq.get(word, 0) + 1
                
        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Return top N keywords
        return [word for word, freq in sorted_words[:top_n]]
    
    def generate_summary(self, text: str, max_length: int = 300) -> str:
        """Generate a summary of the text.
        
        Args:
            text: Input text
            max_length: Maximum length of the summary in words
            
        Returns:
            Summary text
        """
        # In a real implementation, this would use a more sophisticated summarization algorithm
        # For demonstration purposes, we'll use a simple extractive summarization approach
        
        # Preprocess text
        text = self.preprocess_text(text)
        
        # Tokenize into sentences
        sentences = self.tokenize(text)
        
        # Score sentences based on keyword frequency
        keywords = self.extract_keywords(text, top_n=20)
        sentence_scores = {}
        
        for i, sentence in enumerate(sentences):
            score = 0
            words = word_tokenize(sentence.lower())
            
            for word in words:
                if word in keywords:
                    score += 1
                    
            # Normalize by sentence length
            if len(words) > 0:
                score = score / len(words)
                
            sentence_scores[i] = score
            
        # Select top sentences
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Get original sentences in document order
        selected_indices = [idx for idx, score in top_sentences]
        selected_indices.sort()
        
        # Build summary
        summary_sentences = [sentences[idx] for idx in selected_indices]
        summary = ' '.join(summary_sentences)
        
        # Truncate to max length
        words = summary.split()
        if len(words) > max_length:
            summary = ' '.join(words[:max_length]) + '...'
            
        return summary
    
    def extract_key_points(self, text: str, keywords: List[str] = None) -> List[str]:
        """Extract key points from text.
        
        Args:
            text: Input text
            keywords: List of keywords to prioritize
            
        Returns:
            List of key points
        """
        # Tokenize into sentences
        sentences = self.tokenize(text)
        
        # Score sentences based on keywords
        sentence_scores = {}
        
        for i, sentence in enumerate(sentences):
            score = 0
            
            # Check for keywords
            if keywords:
                for keyword in keywords:
                    if keyword.lower() in sentence.lower():
                        score += 2
                        
            # Check for indicator phrases
            indicators = [
                'significant', 'importantly', 'notably', 'key finding',
                'demonstrated', 'revealed', 'showed', 'found', 'observed',
                'conclude', 'conclusion', 'in summary', 'overall'
            ]
            
            for indicator in indicators:
                if indicator in sentence.lower():
                    score += 1
                    
            sentence_scores[i] = score
            
        # Select sentences with scores > 0, sorted by score
        selected = [(i, sentences[i]) for i in sentence_scores if sentence_scores[i] > 0]
        selected.sort(key=lambda x: sentence_scores[x[0]], reverse=True)
        
        # Return top sentences as key points
        return [sentence for _, sentence in selected[:10]]
    
    def extract_clinical_implications(self, text: str) -> List[str]:
        """Extract clinical implications from text.
        
        Args:
            text: Input text
            
        Returns:
            List of clinical implications
        """
        # Tokenize into sentences
        sentences = self.tokenize(text)
        
        # Look for sentences with clinical implication indicators
        implications = []
        
        indicators = [
            'clinical implication', 'clinical practice', 'clinical significance',
            'treatment decision', 'therapeutic implication', 'clinical utility',
            'clinical benefit', 'clinical application', 'clinical relevance',
            'patient care', 'clinical outcome', 'treatment strategy',
            'clinical management', 'therapeutic strategy', 'clinical approach',
            'clinical guideline', 'standard of care', 'clinical recommendation'
        ]
        
        for sentence in sentences:
            for indicator in indicators:
                if indicator in sentence.lower():
                    implications.append(sentence)
                    break
                    
        return implications
    
    def extract_research_directions(self, text: str) -> List[str]:
        """Extract future research directions from text.
        
        Args:
            text: Input text
            
        Returns:
            List of research directions
        """
        # Tokenize into sentences
        sentences = self.tokenize(text)
        
        # Look for sentences with future research indicators
        directions = []
        
        indicators = [
            'future research', 'further research', 'further study', 'further studies',
            'future study', 'future studies', 'future work', 'further work',
            'future investigation', 'further investigation', 'future clinical trial',
            'warrant further', 'remains to be', 'need to be investigated',
            'need for further', 'needs to be explored', 'should be explored'
        ]
        
        for sentence in sentences:
            for indicator in indicators:
                if indicator in sentence.lower():
                    directions.append(sentence)
                    break
                    
        return directions
    
    def extract_treatment_approaches(self, text: str) -> List[str]:
        """Extract treatment approaches from text.
        
        Args:
            text: Input text
            
        Returns:
            List of treatment approaches
        """
        # Tokenize into sentences
        sentences = self.tokenize(text)
        
        # Look for sentences with treatment approach indicators
        approaches = []
        
        indicators = [
            'treatment approach', 'therapeutic approach', 'treatment strategy',
            'therapeutic strategy', 'treatment option', 'therapeutic option',
            'treatment regimen', 'therapeutic regimen', 'treatment protocol',
            'therapeutic protocol', 'treatment algorithm', 'therapeutic algorithm',
            'first-line', 'second-line', 'third-line', 'frontline', 'adjuvant',
            'neoadjuvant', 'maintenance therapy', 'salvage therapy'
        ]
        
        for sentence in sentences:
            for indicator in indicators:
                if indicator in sentence.lower():
                    approaches.append(sentence)
                    break
                    
        return approaches
    
    def extract_topics(self, text: str, num_topics: int = 10) -> List[str]:
        """Extract topics from text.
        
        Args:
            text: Input text
            num_topics: Number of topics to extract
            
        Returns:
            List of topics
        """
        # In a real implementation, this would use a topic modeling algorithm like LDA
        # For demonstration purposes, we'll use a simple keyword extraction approach
        
        # Extract keywords
        keywords = self.extract_keywords(text, top_n=num_topics * 2)
        
        # Group related keywords
        topics = []
        used_keywords = set()
        
        for keyword in keywords:
            if keyword in used_keywords:
                continue
                
            # Find related keywords
            related = [keyword]
            used_keywords.add(keyword)
            
            for other in keywords:
                if other not in used_keywords and (
                    other in keyword or keyword in other or
                    self._are_related(keyword, other)
                ):
                    related.append(other)
                    used_keywords.add(other)
                    
            # Create topic from related keywords
            if len(related) > 1:
                topic = ' / '.join(related[:3])
            else:
                topic = related[0]
                
            topics.append(topic)
            
            if len(topics) >= num_topics:
                break
                
        return topics
    
    def _are_related(self, word1: str, word2: str) -> bool:
        """Check if two words are semantically related.
        
        Args:
            word1: First word
            word2: Second word
            
        Returns:
            True if words are related, False otherwise
        """
        # In a real implementation, this would use word embeddings or a knowledge graph
        # For demonstration purposes, we'll use a simple string similarity approach
        
        # Check for common prefixes
        common_prefix_length = 0
        for i in range(min(len(word1), len(word2))):
            if word1[i] == word2[i]:
                common_prefix_length += 1
            else:
                break
                
        # Consider related if they share a long common prefix
        if common_prefix_length >= 5:
            return True
            
        return False
