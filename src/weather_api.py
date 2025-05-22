import requests
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timedelta
import os
from .utils import load_env_variable

class WeatherAPI:
    """
    Handles all interactions with the OpenWeatherMap API.
    """
    
    def __init__(self):
        """Initialize the WeatherAPI with API key from environment variables."""
        self.api_key = load_env_variable("OPENWEATHERMAP_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
    def get_current_weather(self, location: str, lat: float = None, lon: float = None) -> Dict[str, Any]:
        """
        Get current weather data for a given location.
        
        Args:
            location: Name of the city/location
            lat: Optional latitude for coordinate-based lookup
            lon: Optional longitude for coordinate-based lookup
            
        Returns:
            Dictionary containing weather data
        """
        endpoint = f"{self.base_url}/weather"
        
        # Choose between coordinates or city name based on what's provided
        params = {
            "appid": self.api_key,
            "units": "metric"  # Use metric units (Celsius)
        }
        
        if lat is not None and lon is not None:
            params["lat"] = lat
            params["lon"] = lon
        else:
            params["q"] = location
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch weather data: {str(e)}"
            
            # Check for specific error responses from the API
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 404:
                    error_msg = f"Location '{location}' not found. Please check spelling and try again."
                elif e.response.status_code == 401:
                    error_msg = "Invalid API key. Please check your OpenWeatherMap API key."
            
            raise ValueError(error_msg)
            
    def get_forecast(self, location: str, hours_ahead: int = 24, lat: float = None, lon: float = None) -> Dict[str, Any]:
        """
        Get weather forecast for a given location.
        
        Args:
            location: Name of the city/location
            hours_ahead: Hours ahead to forecast
            lat: Optional latitude for coordinate-based lookup
            lon: Optional longitude for coordinate-based lookup
            
        Returns:
            Dictionary containing forecast data
        """
        endpoint = f"{self.base_url}/forecast"
        
        # Choose between coordinates or city name based on what's provided
        params = {
            "appid": self.api_key,
            "units": "metric",
            "cnt": 8  # Get up to 8 forecast points (24 hours, every 3 hours)
        }
        
        if lat is not None and lon is not None:
            params["lat"] = lat
            params["lon"] = lon
        else:
            params["q"] = location
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Find the forecast closest to the requested hours ahead
            target_time = datetime.now() + timedelta(hours=hours_ahead)
            
            # Extract the relevant forecast point
            forecast_data = None
            closest_diff = float('inf')
            
            for forecast in data.get('list', []):
                forecast_time = datetime.fromtimestamp(forecast['dt'])
                time_diff = abs((forecast_time - target_time).total_seconds())
                
                if time_diff < closest_diff:
                    closest_diff = time_diff
                    forecast_data = forecast
            
            # Add city information to the forecast
            if forecast_data:
                forecast_data['name'] = data.get('city', {}).get('name')
                forecast_data['sys'] = {'country': data.get('city', {}).get('country')}
                
            return forecast_data or {}
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch forecast data: {str(e)}"
            
            # Check for specific error responses
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 404:
                    error_msg = f"Location '{location}' not found. Please check spelling and try again."
                    
            raise ValueError(error_msg)
            
    def get_weather_for_query(self, location: str, is_future: bool, hours_offset: int, lat: float = None, lon: float = None) -> Dict[str, Any]:
        """
        Get weather data based on the natural language query.
        
        Args:
            location: Extracted location from query
            is_future: Whether the query refers to future weather
            hours_offset: Hours from now
            lat: Optional latitude for coordinate-based lookup
            lon: Optional longitude for coordinate-based lookup
            
        Returns:
            Weather data dictionary
        """
        if is_future and hours_offset > 0:
            return self.get_forecast(location, hours_offset, lat, lon)
        else:
            return self.get_current_weather(location, lat, lon)
            
    def get_multi_day_forecast(self, location: str, lat: float = None, lon: float = None) -> Dict[str, Any]:
        """
        Get a 5-day forecast with 3-hour step.
        
        Args:
            location: Name of the city/location
            lat: Optional latitude for coordinate-based lookup
            lon: Optional longitude for coordinate-based lookup
            
        Returns:
            Full forecast data
        """
        endpoint = f"{self.base_url}/forecast"
        
        # Choose between coordinates or city name based on what's provided
        params = {
            "appid": self.api_key,
            "units": "metric",
        }
        
        if lat is not None and lon is not None:
            params["lat"] = lat
            params["lon"] = lon
        else:
            params["q"] = location
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch multi-day forecast: {str(e)}"
            
            # Check for specific error responses
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 404:
                    error_msg = f"Location '{location}' not found. Please check spelling and try again."
                    
            raise ValueError(error_msg)