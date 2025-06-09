"""
Patient profile module for the Oncology AI Assistant System.
Defines data structures for patient information used by the Clinical Trials Agent.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class Location:
    """Patient location information."""
    city: str
    state: str
    country: str = "USA"
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@dataclass
class PatientProfile:
    """Patient profile containing medical and demographic information."""
    patient_id: str
    age: Optional[int] = None
    gender: Optional[str] = None
    cancer_type: Optional[str] = None
    cancer_stage: Optional[str] = None
    biomarkers: Optional[Dict[str, Any]] = None
    prior_treatments: Optional[List[str]] = None
    performance_status: Optional[int] = None
    location: Optional[Location] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert patient profile to dictionary."""
        result = {
            'patient_id': self.patient_id,
            'age': self.age,
            'gender': self.gender,
            'cancer_type': self.cancer_type,
            'cancer_stage': self.cancer_stage,
        }
        
        if self.biomarkers:
            result['biomarkers'] = self.biomarkers
            
        if self.prior_treatments:
            result['prior_treatments'] = self.prior_treatments
            
        if self.performance_status is not None:
            result['performance_status'] = self.performance_status
            
        if self.location:
            result['location'] = {
                'city': self.location.city,
                'state': self.location.state,
                'country': self.location.country,
                'latitude': self.location.latitude,
                'longitude': self.location.longitude
            }
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PatientProfile':
        """Create patient profile from dictionary."""
        location_data = data.get('location')
        location = None
        
        if location_data:
            location = Location(
                city=location_data.get('city', ''),
                state=location_data.get('state', ''),
                country=location_data.get('country', 'USA'),
                latitude=location_data.get('latitude'),
                longitude=location_data.get('longitude')
            )
            
        return cls(
            patient_id=data.get('patient_id', ''),
            age=data.get('age'),
            gender=data.get('gender'),
            cancer_type=data.get('cancer_type'),
            cancer_stage=data.get('cancer_stage'),
            biomarkers=data.get('biomarkers'),
            prior_treatments=data.get('prior_treatments'),
            performance_status=data.get('performance_status'),
            location=location
        )
