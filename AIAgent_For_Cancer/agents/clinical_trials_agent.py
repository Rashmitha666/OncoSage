"""
Clinical Trials Recommendation Agent
Function: Finds active lung cancer trials suitable for a given patient profile.
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from utils.api_clients import ClinicalTrialsClient
from utils.patient_profile import PatientProfile
from utils.geo_utils import calculate_distance

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ClinicalTrialsAgent:
    """Agent that recommends clinical trials based on patient profiles."""
    
    def __init__(self, config_path: str = None):
        """Initialize the clinical trials recommendation agent.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.trials_client = ClinicalTrialsClient()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file."""
        if not config_path:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                      'config', 'clinical_trials_config.json')
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found at {config_path}. Using default configuration.")
            return {
                'max_distance_miles': 100,
                'max_results': 50,
                'default_country': 'United States',
                'include_remote_trials': True,
                'sort_by': 'relevance'  # Options: relevance, distance, start_date
            }
    
    def get_matching_trials(self, patient_profile: PatientProfile) -> List[Dict[str, Any]]:
        """Find clinical trials matching a patient profile.
        
        Args:
            patient_profile: Patient profile containing medical and demographic information
            
        Returns:
            List of matching clinical trials
        """
        logger.info(f"Finding trials for patient with ID: {patient_profile.patient_id}")
        
        # Extract key parameters from patient profile
        search_params = self._build_search_params(patient_profile)
        
        # Search for trials
        all_trials = self.trials_client.search(**search_params)
        
        # Apply additional filters that can't be done via the API
        filtered_trials = self._apply_additional_filters(all_trials, patient_profile)
        
        # Sort trials by relevance score
        sorted_trials = self._sort_trials(filtered_trials, patient_profile)
        
        return sorted_trials
    
    def _build_search_params(self, profile: PatientProfile) -> Dict[str, Any]:
        """Build search parameters from patient profile."""
        params = {
            'condition': 'lung cancer',
            'status': 'recruiting',
            'max_results': self.config.get('max_results', 50),
        }
        
        # Add cancer type specifics
        if profile.cancer_type:
            if 'non-small cell' in profile.cancer_type.lower():
                params['condition'] = 'non-small cell lung cancer'
            elif 'small cell' in profile.cancer_type.lower():
                params['condition'] = 'small cell lung cancer'
        
        # Add location parameters
        if profile.location:
            params['location'] = f"{profile.location.city}, {profile.location.state}"
            params['distance'] = self.config.get('max_distance_miles', 100)
            
        # Add age parameter
        if profile.age:
            params['age'] = profile.age
            
        # Add gender parameter
        if profile.gender:
            params['gender'] = profile.gender
            
        return params
    
    def _apply_additional_filters(self, trials: List[Dict[str, Any]], profile: PatientProfile) -> List[Dict[str, Any]]:
        """Apply additional filters that can't be done via the API."""
        filtered_trials = []
        
        for trial in trials:
            # Check for biomarker/genetic requirements
            if self._matches_biomarkers(trial, profile):
                # Check for treatment history requirements
                if self._matches_treatment_history(trial, profile):
                    # Check for performance status requirements
                    if self._matches_performance_status(trial, profile):
                        filtered_trials.append(trial)
        
        return filtered_trials
    
    def _matches_biomarkers(self, trial: Dict[str, Any], profile: PatientProfile) -> bool:
        """Check if patient's biomarkers match trial requirements."""
        # This is a simplified implementation
        # In a real system, this would parse the trial's eligibility criteria
        
        if not profile.biomarkers:
            # If patient has no biomarker data, we can't confirm a match
            # Some trials might accept patients without specific mutations
            return True
            
        # Check for common lung cancer biomarkers in eligibility
        eligibility_text = trial.get('eligibility_criteria', '').lower()
        
        for biomarker, status in profile.biomarkers.items():
            biomarker_lower = biomarker.lower()
            
            # If trial specifically requires this biomarker
            if biomarker_lower in eligibility_text:
                # Check if trial requires positive and patient is negative or vice versa
                if "positive" in eligibility_text and not status:
                    return False
                if "negative" in eligibility_text and status:
                    return False
                    
        return True
    
    def _matches_treatment_history(self, trial: Dict[str, Any], profile: PatientProfile) -> bool:
        """Check if patient's treatment history matches trial requirements."""
        # This is a simplified implementation
        eligibility_text = trial.get('eligibility_criteria', '').lower()
        
        # Check for treatment-naive requirements
        if "treatment-naive" in eligibility_text or "no prior therapy" in eligibility_text:
            if profile.prior_treatments and len(profile.prior_treatments) > 0:
                return False
                
        # Check for specific prior treatment requirements
        for treatment in profile.prior_treatments:
            # If trial excludes patients who had this treatment
            if f"no prior {treatment.lower()}" in eligibility_text:
                return False
                
        return True
    
    def _matches_performance_status(self, trial: Dict[str, Any], profile: PatientProfile) -> bool:
        """Check if patient's performance status matches trial requirements."""
        if not profile.performance_status:
            return True
            
        eligibility_text = trial.get('eligibility_criteria', '').lower()
        
        # Check for ECOG performance status requirements
        if "ecog" in eligibility_text:
            # Extract required ECOG score from eligibility text
            # This is a simplified implementation
            for i in range(6):  # ECOG scores range from 0-5
                if f"ecog {i}" in eligibility_text or f"ecog performance status {i}" in eligibility_text:
                    required_ecog = i
                    # If patient's ECOG score is higher than required (worse performance)
                    if profile.performance_status > required_ecog:
                        return False
        
        return True
    
    def _sort_trials(self, trials: List[Dict[str, Any]], profile: PatientProfile) -> List[Dict[str, Any]]:
        """Sort trials by relevance to the patient."""
        sort_by = self.config.get('sort_by', 'relevance')
        
        if sort_by == 'distance' and profile.location:
            # Sort by distance to patient
            for trial in trials:
                if 'location' in trial:
                    trial['distance'] = calculate_distance(
                        profile.location.latitude, 
                        profile.location.longitude,
                        trial['location'].get('latitude'),
                        trial['location'].get('longitude')
                    )
            return sorted(trials, key=lambda x: x.get('distance', float('inf')))
            
        elif sort_by == 'start_date':
            # Sort by start date (newest first)
            return sorted(trials, key=lambda x: x.get('start_date', ''), reverse=True)
            
        else:
            # Sort by relevance (default)
            # This would involve a more complex scoring algorithm in a real system
            return trials
    
    def generate_trial_recommendations(self, patient_profile: PatientProfile) -> Dict[str, Any]:
        """Generate trial recommendations for a patient.
        
        Args:
            patient_profile: Patient profile containing medical and demographic information
            
        Returns:
            Dictionary containing recommendations and metadata
        """
        matching_trials = self.get_matching_trials(patient_profile)
        
        recommendations = {
            'timestamp': datetime.now().isoformat(),
            'patient_id': patient_profile.patient_id,
            'trials_count': len(matching_trials),
            'trials': matching_trials,
            'search_criteria': self._build_search_params(patient_profile)
        }
        
        return recommendations

if __name__ == "__main__":
    # For testing purposes
    from utils.patient_profile import PatientProfile, Location
    
    # Create a sample patient profile
    location = Location(city="Boston", state="MA", country="USA", 
                       latitude=42.3601, longitude=-71.0589)
    
    profile = PatientProfile(
        patient_id="TEST001",
        age=65,
        gender="Female",
        cancer_type="Non-small cell lung cancer",
        cancer_stage="Stage IIIB",
        biomarkers={"EGFR": True, "ALK": False, "PD-L1": 80},
        prior_treatments=["Carboplatin", "Pemetrexed"],
        performance_status=1,
        location=location
    )
    
    # Test the agent
    agent = ClinicalTrialsAgent()
    recommendations = agent.generate_trial_recommendations(profile)
    
    print(f"Found {recommendations['trials_count']} matching trials for patient {profile.patient_id}")
