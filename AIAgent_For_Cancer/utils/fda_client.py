"""
FDA API client for the Oncology AI Assistant System.
Provides functionality to search and retrieve drug safety information from the FDA.
"""
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FDAClient:
    """Client for interacting with the FDA API."""
    
    def __init__(self, api_key: str = None):
        """Initialize the FDA API client.
        
        Args:
            api_key: Optional API key for higher rate limits
        """
        self.base_url = "https://api.fda.gov"
        self.api_key = api_key
        
    def get_drug_alerts(self, drug_name: str, days_lookback: int = 90, 
                       limit: int = 100) -> List[Dict[str, Any]]:
        """Get safety alerts for a specific drug.
        
        Args:
            drug_name: Name of the drug
            days_lookback: Number of days to look back
            limit: Maximum number of results to return
            
        Returns:
            List of drug alert dictionaries
        """
        logger.info(f"Checking FDA alerts for drug: {drug_name}")
        
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_lookback)
            
            # Format dates for FDA API
            start_date_str = start_date.strftime("%Y%m%d")
            
            # In a real implementation, this would use the FDA API
            # For demonstration purposes, we'll return placeholder data
            
            return [
                {
                    "id": "FDA-2025-N-0001",
                    "type": "safety_alert",
                    "title": f"FDA Safety Alert for {drug_name}",
                    "description": f"The FDA has issued a safety alert for {drug_name} related to potential side effects.",
                    "date": (end_date - timedelta(days=5)).strftime("%Y-%m-%d"),
                    "url": f"https://www.fda.gov/drugs/drug-safety-and-availability/{drug_name.lower()}-safety-alert",
                    "severity": "medium"
                }
            ]
            
        except Exception as e:
            logger.error(f"Error getting FDA alerts: {e}")
            return []
    
    def search_drug_events(self, drug_name: str, days_lookback: int = 90, 
                          limit: int = 100) -> List[Dict[str, Any]]:
        """Search for adverse events for a specific drug.
        
        Args:
            drug_name: Name of the drug
            days_lookback: Number of days to look back
            limit: Maximum number of results to return
            
        Returns:
            List of adverse event dictionaries
        """
        logger.info(f"Searching FDA adverse events for drug: {drug_name}")
        
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_lookback)
            
            # Format dates for FDA API
            start_date_str = start_date.strftime("%Y%m%d")
            
            # Construct search query
            query = f"patient.drug.medicinalproduct:{drug_name}"
            query += f"+AND+receivedate:[{start_date_str}+TO+999999999999]"
            
            # Build request URL
            url = f"{self.base_url}/drug/event.json"
            params = {
                "search": query,
                "limit": limit
            }
            
            if self.api_key:
                params["api_key"] = self.api_key
                
            # Make request
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            results = data.get("results", [])
            
            logger.info(f"Found {len(results)} adverse events for {drug_name}")
            
            # Process results
            events = []
            for result in results:
                event = self._process_event(result, drug_name)
                if event:
                    events.append(event)
                    
            return events
            
        except Exception as e:
            logger.error(f"Error searching FDA adverse events: {e}")
            return []
    
    def search_drug_recalls(self, drug_name: str, days_lookback: int = 365, 
                           limit: int = 100) -> List[Dict[str, Any]]:
        """Search for recalls for a specific drug.
        
        Args:
            drug_name: Name of the drug
            days_lookback: Number of days to look back
            limit: Maximum number of results to return
            
        Returns:
            List of recall dictionaries
        """
        logger.info(f"Searching FDA recalls for drug: {drug_name}")
        
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_lookback)
            
            # Format dates for FDA API
            start_date_str = start_date.strftime("%Y%m%d")
            
            # Construct search query
            query = f"product_description:{drug_name}"
            query += f"+AND+recall_initiation_date:[{start_date_str}+TO+999999999999]"
            
            # Build request URL
            url = f"{self.base_url}/drug/enforcement.json"
            params = {
                "search": query,
                "limit": limit
            }
            
            if self.api_key:
                params["api_key"] = self.api_key
                
            # Make request
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            results = data.get("results", [])
            
            logger.info(f"Found {len(results)} recalls for {drug_name}")
            
            # Process results
            recalls = []
            for result in results:
                recall = self._process_recall(result)
                if recall:
                    recalls.append(recall)
                    
            return recalls
            
        except Exception as e:
            logger.error(f"Error searching FDA recalls: {e}")
            return []
    
    def search_drug_labels(self, drug_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for drug labels for a specific drug.
        
        Args:
            drug_name: Name of the drug
            limit: Maximum number of results to return
            
        Returns:
            List of drug label dictionaries
        """
        logger.info(f"Searching FDA drug labels for drug: {drug_name}")
        
        try:
            # Construct search query
            query = f"openfda.generic_name:{drug_name}+OR+openfda.brand_name:{drug_name}"
            
            # Build request URL
            url = f"{self.base_url}/drug/label.json"
            params = {
                "search": query,
                "limit": limit
            }
            
            if self.api_key:
                params["api_key"] = self.api_key
                
            # Make request
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            results = data.get("results", [])
            
            logger.info(f"Found {len(results)} drug labels for {drug_name}")
            
            # Process results
            labels = []
            for result in results:
                label = self._process_label(result)
                if label:
                    labels.append(label)
                    
            return labels
            
        except Exception as e:
            logger.error(f"Error searching FDA drug labels: {e}")
            return []
    
    def get_black_box_warnings(self, drug_name: str) -> List[Dict[str, Any]]:
        """Get black box warnings for a specific drug.
        
        Args:
            drug_name: Name of the drug
            
        Returns:
            List of black box warning dictionaries
        """
        logger.info(f"Getting black box warnings for drug: {drug_name}")
        
        try:
            # Get drug labels
            labels = self.search_drug_labels(drug_name)
            
            # Extract black box warnings
            warnings = []
            for label in labels:
                boxed_warning = label.get("boxed_warning")
                if boxed_warning:
                    warnings.append({
                        "drug_name": label.get("drug_name", drug_name),
                        "warning": boxed_warning,
                        "source": "FDA",
                        "url": label.get("url", "")
                    })
                    
            logger.info(f"Found {len(warnings)} black box warnings for {drug_name}")
            return warnings
            
        except Exception as e:
            logger.error(f"Error getting black box warnings: {e}")
            return []
    
    def _process_event(self, event: Dict[str, Any], drug_name: str) -> Optional[Dict[str, Any]]:
        """Process an adverse event from the FDA API.
        
        Args:
            event: Raw event data from API
            drug_name: Name of the drug
            
        Returns:
            Processed event dictionary
        """
        try:
            # Extract patient information
            patient = event.get("patient", {})
            
            # Extract reaction information
            reactions = []
            for reaction in patient.get("reaction", []):
                reaction_term = reaction.get("reactionmeddrapt")
                if reaction_term:
                    reactions.append(reaction_term)
                    
            # Extract drug information
            drugs = []
            for drug in patient.get("drug", []):
                drug_info = {
                    "name": drug.get("medicinalproduct", "Unknown"),
                    "indication": drug.get("drugindication", ""),
                    "dosage": drug.get("drugdosagetext", ""),
                    "route": drug.get("drugadministrationroute", "")
                }
                drugs.append(drug_info)
                
            # Extract report information
            report_date = event.get("receiptdate", "")
            if report_date:
                report_date = f"{report_date[:4]}-{report_date[4:6]}-{report_date[6:8]}"
                
            # Return processed event
            return {
                "report_id": event.get("safetyreportid", "Unknown"),
                "report_date": report_date,
                "serious": event.get("serious", "0") == "1",
                "reactions": reactions,
                "drugs": drugs,
                "source": "FDA Adverse Event Reporting System",
                "url": f"https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=overview.process&ApplNo={event.get('safetyreportid', '')}"
            }
            
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            return None
    
    def _process_recall(self, recall: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a recall from the FDA API.
        
        Args:
            recall: Raw recall data from API
            
        Returns:
            Processed recall dictionary
        """
        try:
            # Extract recall information
            recall_date = recall.get("recall_initiation_date", "")
            if recall_date:
                recall_date = f"{recall_date[:4]}-{recall_date[4:6]}-{recall_date[6:8]}"
                
            # Return processed recall
            return {
                "recall_number": recall.get("recall_number", "Unknown"),
                "recall_date": recall_date,
                "product": recall.get("product_description", "Unknown"),
                "reason": recall.get("reason_for_recall", ""),
                "classification": recall.get("classification", ""),
                "status": recall.get("status", ""),
                "source": "FDA Enforcement Reports",
                "url": f"https://www.accessdata.fda.gov/scripts/ires/index.cfm?Event=RecallDetails&RecallID={recall.get('recall_number', '')}"
            }
            
        except Exception as e:
            logger.error(f"Error processing recall: {e}")
            return None
    
    def _process_label(self, label: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a drug label from the FDA API.
        
        Args:
            label: Raw label data from API
            
        Returns:
            Processed label dictionary
        """
        try:
            # Extract OpenFDA information
            openfda = label.get("openfda", {})
            
            # Get drug name
            brand_name = openfda.get("brand_name", ["Unknown"])[0] if openfda.get("brand_name") else "Unknown"
            generic_name = openfda.get("generic_name", [""])[0] if openfda.get("generic_name") else ""
            
            drug_name = brand_name
            if generic_name and generic_name != brand_name:
                drug_name = f"{brand_name} ({generic_name})"
                
            # Extract warnings
            warnings = label.get("warnings", [""])[0] if label.get("warnings") else ""
            boxed_warning = label.get("boxed_warning", [""])[0] if label.get("boxed_warning") else ""
            
            # Extract adverse reactions
            adverse_reactions = label.get("adverse_reactions", [""])[0] if label.get("adverse_reactions") else ""
            
            # Return processed label
            return {
                "drug_name": drug_name,
                "manufacturer": openfda.get("manufacturer_name", ["Unknown"])[0] if openfda.get("manufacturer_name") else "Unknown",
                "warnings": warnings,
                "boxed_warning": boxed_warning,
                "adverse_reactions": adverse_reactions,
                "source": "FDA Drug Labels",
                "url": f"https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid={openfda.get('spl_set_id', [''])[0]}" if openfda.get("spl_set_id") else ""
            }
            
        except Exception as e:
            logger.error(f"Error processing label: {e}")
            return None
