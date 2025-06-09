"""
Geographic utilities for the Oncology AI Assistant System.
Provides functions for calculating distances and working with locations.
"""
import math
from typing import Tuple, Optional


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the distance between two points on Earth using the Haversine formula.
    
    Args:
        lat1: Latitude of the first point in degrees
        lon1: Longitude of the first point in degrees
        lat2: Latitude of the second point in degrees
        lon2: Longitude of the second point in degrees
        
    Returns:
        Distance in miles
    """
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    # Radius of Earth in miles
    radius = 3958.8
    
    # Calculate distance
    distance = radius * c
    
    return distance


def get_coordinates_from_address(address: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Get latitude and longitude coordinates from an address string.
    This is a placeholder function that would typically use a geocoding API.
    
    Args:
        address: Address string (e.g., "Boston, MA")
        
    Returns:
        Tuple of (latitude, longitude) or (None, None) if not found
    """
    # In a real implementation, this would call a geocoding API like Google Maps or Nominatim
    # For demonstration purposes, we'll return hardcoded values for some common cities
    
    address_lower = address.lower()
    
    # Some hardcoded coordinates for common cities
    if "boston" in address_lower and "ma" in address_lower:
        return 42.3601, -71.0589
    elif "new york" in address_lower or "nyc" in address_lower:
        return 40.7128, -74.0060
    elif "los angeles" in address_lower or "la" in address_lower:
        return 34.0522, -118.2437
    elif "chicago" in address_lower:
        return 41.8781, -87.6298
    elif "houston" in address_lower:
        return 29.7604, -95.3698
    elif "philadelphia" in address_lower:
        return 39.9526, -75.1652
    elif "phoenix" in address_lower:
        return 33.4484, -112.0740
    elif "san francisco" in address_lower or "sf" in address_lower:
        return 37.7749, -122.4194
    elif "seattle" in address_lower:
        return 47.6062, -122.3321
    elif "miami" in address_lower:
        return 25.7617, -80.1918
    
    # Return None for unknown locations
    return None, None


def get_nearby_locations(lat: float, lon: float, radius_miles: float = 50) -> list:
    """
    Get nearby locations within a specified radius.
    This is a placeholder function that would typically use a locations API.
    
    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        radius_miles: Radius in miles to search
        
    Returns:
        List of nearby locations
    """
    # In a real implementation, this would call a locations API
    # For demonstration purposes, we'll return an empty list
    return []
