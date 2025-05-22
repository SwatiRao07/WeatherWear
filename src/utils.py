import os
import re
import json
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
from colorama import Fore, Style, init
import requests
from geopy.geocoders import Nominatim

# Initialize colorama for cross-platform colored terminal output
init(autoreset=True)

def load_env_variable(var_name: str, default: str = None) -> str:
    """
    Safely load an environment variable with optional default value.
    """
    value = os.getenv(var_name, default)
    if value is None:
        raise ValueError(f"Environment variable {var_name} not set and no default provided.")
    return value

def parse_time_from_query(query: str) -> Tuple[bool, int]:
    """
    Extract time information from a user query.
    
    Returns:
        Tuple[bool, int]: (is_future, hours_offset)
        - is_future: Whether the query refers to a future time
        - hours_offset: Hours from now (0 for current)
    """
    # Default to current time
    is_future = False
    hours_offset = 0
    
    # Look for time indicators
    query_lower = query.lower()
    
    # Check for future indicators
    future_indicators = ["tomorrow", "next", "later", "upcoming", "evening", "night", "afternoon", "morning"]
    if any(indicator in query_lower for indicator in future_indicators):
        is_future = True
        
        # Determine approximate hours offset
        if "tomorrow" in query_lower:
            hours_offset = 24
            
            # Refine by time of day
            if "morning" in query_lower:
                hours_offset = 24  # Default to 24 hours if just "tomorrow morning"
            elif "afternoon" in query_lower:
                hours_offset = 30  # Roughly 6 hours past morning
            elif "evening" in query_lower or "night" in query_lower:
                hours_offset = 36  # Roughly 12 hours past morning
        
        elif "evening" in query_lower or "night" in query_lower:
            # If just evening today
            current_hour = datetime.now().hour
            if current_hour < 18:  # If it's before 6 PM
                hours_offset = 18 - current_hour
            else:
                hours_offset = 0  # Already evening
        
        elif "afternoon" in query_lower:
            current_hour = datetime.now().hour
            if current_hour < 12:  # If it's before noon
                hours_offset = 12 - current_hour
            else:
                hours_offset = 0  # Already afternoon
    
    return is_future, hours_offset

def extract_location(query: str) -> str:
    """
    Extract the most likely location from a user query.
    Basic implementation - for complex queries, consider NLP libraries.
    """
    # Check for location shorthand terms that need geolocation
    location_shortcuts = ["here", "my location", "my city", "current location", "my area", "where i am", "current position"]
    query_lower = query.lower()
    
    for shortcut in location_shortcuts:
        if shortcut in query_lower:
            return "CURRENT_LOCATION"
    
    # Strip out common time-related phrases
    time_phrases = ["tomorrow", "today", "this afternoon", "this evening", 
                   "tonight", "in the morning", "next week", "weekend"]
    
    cleaned_query = query_lower
    for phrase in time_phrases:
        cleaned_query = cleaned_query.replace(phrase, "")
    
    # Remove prepositions and articles
    words = cleaned_query.split()
    filtered_words = [w for w in words if w not in ["in", "at", "for", "the", "a", "an"]]
    
    # Rejoin remaining words - this is likely our location
    return " ".join(filtered_words).strip()

def colorize_weather(weather_data: Dict[str, Any]) -> str:
    """
    Format weather data with colorized output.
    """
    # Extract relevant data
    temp = weather_data.get("main", {}).get("temp", "N/A")
    feels_like = weather_data.get("main", {}).get("feels_like", "N/A")
    humidity = weather_data.get("main", {}).get("humidity", "N/A")
    wind_speed = weather_data.get("wind", {}).get("speed", "N/A")
    conditions = weather_data.get("weather", [{}])[0].get("description", "N/A") if weather_data.get("weather") else "N/A"
    location = f"{weather_data.get('name', 'Unknown')}, {weather_data.get('sys', {}).get('country', '')}"
    
    # Format output with colors
    output = [
        f"Weather in {Fore.CYAN}{location}{Style.RESET_ALL}:",
        f"🌡️ Temperature: {Fore.YELLOW}{temp}°C{Style.RESET_ALL} (feels like {feels_like}°C)",
        f"💧 Humidity: {Fore.BLUE}{humidity}%{Style.RESET_ALL}",
        f"💨 Wind: {Fore.GREEN}{wind_speed} km/h{Style.RESET_ALL}",
        f"☁️ Conditions: {Fore.MAGENTA}{conditions.title()}{Style.RESET_ALL}"
    ]
    
    return "\n".join(output)

def format_outfit_recommendation(recommendation: str) -> str:
    """
    Format the outfit recommendation with colors.
    """
    return f"\n{Fore.GREEN}Outfit recommendation:{Style.RESET_ALL}\n{recommendation}"

def validate_style_preference(preference: str) -> str:
    """
    Validate and normalize style preference.
    """
    valid_styles = ["casual", "formal", "sporty"]
    preference = preference.lower().strip()
    
    if preference in valid_styles:
        return preference
    elif not preference:
        return "casual"  # Default
    else:
        print(f"{Fore.YELLOW}Warning: '{preference}' is not a recognized style. Using 'casual' instead.{Style.RESET_ALL}")
        return "casual"

def get_current_location() -> Tuple[str, float, float]:
    """
    Get the user's current location using IP-based geolocation.
    
    Returns:
        Tuple[str, float, float]: (location_name, latitude, longitude)
    """
    try:
        # Use ipinfo.io to get location based on IP (no API key required for basic usage)
        response = requests.get('https://ipinfo.io/json')
        data = response.json()
        
        # Extract location data
        location = data.get('city', 'Unknown')
        country = data.get('country', '')
        if country:
            location = f"{location}, {country}"
            
        # Extract coordinates
        coords = data.get('loc', '0,0').split(',')
        lat = float(coords[0])
        lng = float(coords[1])
        
        # Use reverse geocoding to get a more detailed location name
        geolocator = Nominatim(user_agent="weatherwear")
        try:
            address = geolocator.reverse(f"{lat}, {lng}")
            if address:
                city = address.raw.get('address', {}).get('city')
                if city:
                    location = city
        except:
            # If reverse geocoding fails, use the IP-based city
            pass
            
        return location, lat, lng
        
    except Exception as e:
        print(f"{Fore.YELLOW}Warning: Could not determine current location. {str(e)}{Style.RESET_ALL}")
        # Return a default value
        return "New York", 40.7128, -74.0060  # Default to New York if geolocation fails

def format_forecast_display(forecast_data: Dict[str, Any]) -> str:
    """
    Format multi-day forecast data for display.
    
    Args:
        forecast_data: Weather forecast data
        
    Returns:
        Formatted forecast string
    """
    if not forecast_data or 'list' not in forecast_data:
        return "No forecast data available"
    
    # Group forecasts by day
    days = {}
    for item in forecast_data['list']:
        dt = datetime.fromtimestamp(item['dt'])
        day_key = dt.strftime('%Y-%m-%d')
        
        if day_key not in days:
            days[day_key] = []
            
        days[day_key].append(item)
    
    # Format output
    output = [f"\n{Fore.CYAN}5-Day Forecast for {forecast_data.get('city', {}).get('name')}:{Style.RESET_ALL}"]
    
    for day_key in sorted(days.keys()):
        day_items = days[day_key]
        day_date = datetime.strptime(day_key, '%Y-%m-%d')
        day_name = day_date.strftime('%A')
        
        # Get mid-day forecast for the day (around noon)
        mid_day = None
        for item in day_items:
            item_hour = datetime.fromtimestamp(item['dt']).hour
            if 11 <= item_hour <= 14:
                mid_day = item
                break
        
        # If no mid-day forecast, use the first one
        if not mid_day and day_items:
            mid_day = day_items[0]
            
        if mid_day:
            temp = mid_day['main']['temp']
            weather = mid_day['weather'][0]['description'] 
            item_time = datetime.fromtimestamp(mid_day['dt']).strftime('%H:%M')
            
            output.append(f"{Fore.YELLOW}{day_name} ({day_date.strftime('%d %b')}):{Style.RESET_ALL} {Fore.WHITE}{temp}°C, {weather}{Style.RESET_ALL}")
    
    return "\n".join(output)