"""
ClinicalTrials.gov API client for the Oncology AI Assistant System.
Provides functionality to search and retrieve clinical trial information.
"""
import logging
import requests
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ClinicalTrialsClient:
    """Client for interacting with the ClinicalTrials.gov API."""
    
    def __init__(self):
        """Initialize the ClinicalTrials.gov API client."""
        self.base_url = "https://clinicaltrials.gov/api/v2/studies"
        
    def search(self, query: str = None, condition: str = None, intervention: str = None, 
              location: str = None, distance: int = None, status: str = None, 
              phase: str = None, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search for clinical trials matching the criteria.
        
        Args:
            query: General search query
            condition: Medical condition (e.g., "lung cancer")
            intervention: Treatment intervention
            location: Geographic location
            distance: Distance from location in miles
            status: Trial status (e.g., "recruiting")
            phase: Trial phase (e.g., "phase 1", "phase 2")
            max_results: Maximum number of results to return
            
        Returns:
            List of clinical trial dictionaries
        """
        logger.info(f"Searching clinical trials for condition: {condition}, query: {query}")
        
        # Build query parameters
        params = {
            "format": "json",
            "pageSize": max_results
        }
        
        # Add search criteria
        query_terms = []
        
        if query:
            query_terms.append(query)
            
        if condition:
            query_terms.append(f"CONDITION:{condition}")
            
        if intervention:
            query_terms.append(f"INTERVENTION:{intervention}")
            
        if status:
            query_terms.append(f"STATUS:{status}")
            
        if phase:
            query_terms.append(f"PHASE:{phase}")
            
        if query_terms:
            params["query"] = " AND ".join(query_terms)
            
        # Add location parameters
        if location:
            params["location"] = location
            
            if distance:
                params["distance"] = distance
        
        try:
            # Make API request
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            studies = data.get("studies", [])
            
            logger.info(f"Found {len(studies)} clinical trials matching criteria")
            
            # Process and return studies
            return [self._process_study(study) for study in studies]
            
        except Exception as e:
            logger.error(f"Error searching clinical trials: {e}")
            return []
    
    def get_trial(self, nct_id: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific clinical trial by NCT ID.
        
        Args:
            nct_id: ClinicalTrials.gov identifier (NCT number)
            
        Returns:
            Dictionary with trial information
        """
        logger.info(f"Fetching clinical trial with ID: {nct_id}")
        
        try:
            # Make API request
            url = f"{self.base_url}/{nct_id}"
            response = requests.get(url, params={"format": "json"})
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            # Process and return study
            return self._process_study(data)
            
        except Exception as e:
            logger.error(f"Error fetching clinical trial {nct_id}: {e}")
            return None
    
    def search_lung_cancer_trials(self, biomarkers: List[str] = None, 
                                 recruiting_only: bool = True, 
                                 location: str = None, 
                                 distance: int = 100,
                                 max_results: int = 50) -> List[Dict[str, Any]]:
        """Search for lung cancer clinical trials with specific criteria.
        
        Args:
            biomarkers: List of biomarkers to search for
            recruiting_only: Whether to include only recruiting trials
            location: Geographic location
            distance: Distance from location in miles
            max_results: Maximum number of results to return
            
        Returns:
            List of clinical trial dictionaries
        """
        # Build query for lung cancer
        query = "CONDITION:lung cancer OR CONDITION:NSCLC OR CONDITION:SCLC"
        
        # Add biomarkers to query if provided
        if biomarkers:
            biomarker_terms = []
            for biomarker in biomarkers:
                biomarker_terms.append(f"BIOMARKER:{biomarker}")
            query += " AND (" + " OR ".join(biomarker_terms) + ")"
            
        # Set status for recruiting trials
        status = "RECRUITING" if recruiting_only else None
        
        # Search for trials
        trials = self.search(
            query=query,
            status=status,
            location=location,
            distance=distance,
            max_results=max_results
        )
        
        return trials
    
    def _process_study(self, study: Dict[str, Any]) -> Dict[str, Any]:
        """Process and extract relevant information from a study.
        
        Args:
            study: Raw study data from API
            
        Returns:
            Processed study dictionary
        """
        protocol = study.get("protocolSection", {})
        
        # Extract identification information
        identification = protocol.get("identificationModule", {})
        nct_id = identification.get("nctId", "Unknown")
        title = identification.get("briefTitle", "Unknown")
        official_title = identification.get("officialTitle", title)
        
        # Extract status information
        status_module = protocol.get("statusModule", {})
        status = status_module.get("overallStatus", "Unknown")
        phase = protocol.get("designModule", {}).get("phases", ["Unknown"])[0] if protocol.get("designModule", {}).get("phases") else "Unknown"
        
        # Extract eligibility information
        eligibility = protocol.get("eligibilityModule", {})
        criteria = eligibility.get("eligibilityCriteria", "")
        gender = eligibility.get("gender", "Unknown")
        min_age = eligibility.get("minimumAge", "Unknown")
        max_age = eligibility.get("maximumAge", "Unknown")
        
        # Extract location information
        contacts = protocol.get("contactsLocationsModule", {})
        locations = contacts.get("locations", [])
        location_list = []
        
        for location in locations:
            location_list.append({
                "facility": location.get("facility", {}).get("name", "Unknown"),
                "city": location.get("city", "Unknown"),
                "state": location.get("state", "Unknown"),
                "country": location.get("country", "Unknown"),
                "zip": location.get("zip", "Unknown"),
                "status": location.get("status", "Unknown")
            })
            
        # Extract intervention information
        arms = protocol.get("armsInterventionsModule", {}).get("interventions", [])
        interventions = []
        
        for arm in arms:
            interventions.append({
                "type": arm.get("type", "Unknown"),
                "name": arm.get("name", "Unknown"),
                "description": arm.get("description", "")
            })
            
        # Extract biomarker information
        biomarkers = []
        biomarker_section = protocol.get("biospecimenModule", {}).get("biospecimenDescription", "")
        
        # In a real implementation, this would use NLP to extract biomarkers from the description
        # For demonstration purposes, we'll just check for common lung cancer biomarkers
        common_biomarkers = ["EGFR", "ALK", "ROS1", "BRAF", "KRAS", "MET", "RET", "NTRK", "PD-L1"]
        for biomarker in common_biomarkers:
            if biomarker in biomarker_section or biomarker in criteria:
                biomarkers.append(biomarker)
        
        # Return processed study
        return {
            "nct_id": nct_id,
            "title": title,
            "official_title": official_title,
            "status": status,
            "phase": phase,
            "conditions": protocol.get("conditionsModule", {}).get("conditions", []),
            "biomarkers": biomarkers,
            "eligibility_criteria": criteria,
            "gender": gender,
            "age_range": f"{min_age} - {max_age}",
            "locations": location_list,
            "interventions": interventions,
            "url": f"https://clinicaltrials.gov/study/{nct_id}"
        }
