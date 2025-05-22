from typing import Dict, Any, Optional, Tuple, List
from .weather_api import WeatherAPI
from .llm_api import LLMClient
from .utils import parse_time_from_query, extract_location, colorize_weather, format_outfit_recommendation, get_current_location, format_forecast_display
from colorama import Fore, Style

class OutfitGenerator:
    """
    Core class that orchestrates the outfit recommendation process.
    """
    
    def __init__(self):
        """Initialize the OutfitGenerator with required components."""
        self.weather_api = WeatherAPI()
        self.llm_client = LLMClient()
        
    def process_query(self, query: str, style_preference: str, show_forecast: bool = False) -> Tuple[str, str, str]:
        """
        Process a natural language query and generate outfit recommendations.
        
        Args:
            query: Natural language query for location and time
            style_preference: User's style preference
            show_forecast: Whether to include multi-day forecast
            
        Returns:
            Tuple containing weather data, outfit recommendation, and forecast (if requested)
        """
        # Parse time information from query
        is_future, hours_offset = parse_time_from_query(query)
        
        # Extract location from query
        location = extract_location(query)
        
        lat, lon = None, None
        if not location:
            raise ValueError("Couldn't identify a location in your query. Please try again with a clearer location.")
        
        # Handle special case for current location
        if location == "CURRENT_LOCATION":
            location, lat, lon = get_current_location()
            print(f"{Fore.GREEN}📍 Using your current location: {Fore.CYAN}{location}{Style.RESET_ALL}")
        
        # Get weather data
        weather_data = self.weather_api.get_weather_for_query(location, is_future, hours_offset, lat, lon)
        
        # Format weather information for display
        weather_info = colorize_weather(weather_data)
        
        # Generate enhanced outfit recommendation using the LLMClient's enhanced method
        try:
            outfit_recommendation = self._generate_enhanced_outfit_recommendation(
                weather_data=weather_data,
                location=location,
                style_preference=style_preference,
                is_future=is_future
            )
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  LLM generation failed: {e}{Style.RESET_ALL}")
            # Use the LLMClient's fallback method which already has the enhanced format
            outfit_recommendation = self.llm_client._create_fallback_recommendation(weather_data, location, style_preference)
        
        # Format outfit recommendation with enhanced header
        formatted_recommendation = self._format_enhanced_recommendation(outfit_recommendation, weather_data, location, style_preference)
        
        # Get and format forecast data if requested
        forecast_info = ""
        if show_forecast:
            try:
                forecast_data = self.weather_api.get_multi_day_forecast(location, lat, lon)
                forecast_info = format_forecast_display(forecast_data)
            except Exception as e:
                forecast_info = f"\n{Fore.YELLOW}⚠️  Could not retrieve extended forecast: {str(e)}{Style.RESET_ALL}"
        
        return weather_info, formatted_recommendation, forecast_info
    
    def _generate_enhanced_outfit_recommendation(self, weather_data: Dict[str, Any], location: str, style_preference: str, is_future: bool) -> str:
        """Generate an enhanced outfit recommendation with detailed formatting."""
        # Use the LLMClient's generate_outfit_recommendation method which already has enhanced prompting
        recommendation = self.llm_client.generate_outfit_recommendation(
            weather_data=weather_data,
            location=location,
            style_preference=style_preference,
            is_future=is_future
        )
        
        # If the recommendation doesn't have the proper format, try again with direct prompt
        if "🎽" not in recommendation:
            # Extract weather information for custom prompt
            temp = weather_data.get("main", {}).get("temp", "unknown")
            feels_like = weather_data.get("main", {}).get("feels_like", "unknown")
            humidity = weather_data.get("main", {}).get("humidity", "unknown")
            wind_speed = weather_data.get("wind", {}).get("speed", "unknown")
            conditions = weather_data.get("weather", [{}])[0].get("description", "unknown") if weather_data.get("weather") else "unknown"
            weather_location = weather_data.get("name", location)
            country = weather_data.get("sys", {}).get("country", "")
            
            # Create ultra-creative prompt for diverse recommendations
            creative_prompt = f"""
            You are WeatherWear, the world's most creative and diverse fashion stylist who creates stunning, unique outfit recommendations. 
            Create an absolutely captivating outfit recommendation for {weather_location}, {country} with this weather:
            - Temperature: {temp}°C (feels like {feels_like}°C)
            - Humidity: {humidity}%
            - Wind: {wind_speed} km/h
            - Conditions: {conditions}
            - Style: {style_preference}
            
            Be EXTREMELY creative, diverse, and impressive. Use vivid language, unexpected combinations, and trendy details.
            
            Structure your response EXACTLY like this format:
            
            🎽 Your Look, Tailored to [Creative Weather Description] & [Location Vibe]
            [Poetic weather mood description with personality and flair]
            
            🧢 Top Layer: [Ultra-specific trendy item with creative description and styling details]
            👕 Mid-Layer: [Innovative layering piece with color/texture details and style reasoning]  
            👖 Bottoms: [Fashion-forward bottom with cut, fit, and trend details]
            👟 Shoes: [Stylish footwear with brand vibes and weather-specific features]
            🧤 Accessories: [2-3 statement accessories with styling impact and practical benefits]
            
            🧠 Smart Layering Tip:
            [Professional styling secret with specific technique for the weather and style - be detailed and expert-level]
            
            🌍 Local Flavor Add-On:
            [Cultural fashion insight specific to the location with local style trends and colors]
            
            🎒 Your Pack & Prep List:
            [6 practical items with emojis, each with specific brand vibes or creative descriptions]
            
            🎵 [Ultra-creative playlist name mixing weather/location/style] 🎧
            
            💬 Confidence Closer:
            [Motivational, inspiring closer that makes them feel like a fashion icon. End with a powerful quote in quotes.]
            
            Make this recommendation UNFORGETTABLE - use unexpected color combinations, trendy pieces, street style inspiration, and make them feel like they're walking a runway in {weather_location}!
            """
            
            # Try to generate with the creative prompt
            if self.llm_client.client is not None:
                try:
                    chat_completion = self.llm_client.client.chat.completions.create(
                        messages=[{"role": "user", "content": creative_prompt}],
                        model=self.llm_client.model,
                        temperature=0.9,  # Higher creativity
                        max_tokens=1000,  # More space for creativity
                        top_p=0.95
                    )
                    recommendation = chat_completion.choices[0].message.content.strip()
                except Exception as e:
                    print(f"{Fore.YELLOW}⚠️  Creative prompt failed: {e}{Style.RESET_ALL}")
                    # Fall back to the LLMClient's fallback
                    recommendation = self.llm_client._create_fallback_recommendation(weather_data, location, style_preference)
        
        return recommendation
    
    def _format_enhanced_recommendation(self, recommendation: str, weather_data: Dict[str, Any], location: str, style_preference: str) -> str:
        """Format the recommendation with enhanced header and beautiful styling."""
        weather_location = weather_data.get("name", location)
        country = weather_data.get("sys", {}).get("country", "")
        conditions = weather_data.get("weather", [{}])[0].get("description", "unknown") if weather_data.get("weather") else "unknown"
        temp = weather_data.get("main", {}).get("temp", "unknown")
        wind_speed = weather_data.get("wind", {}).get("speed", "unknown")
        
        # Create sophisticated mood tags based on conditions and style
        mood_tags = {
            ("casual", "clear"): "Effortless Sunshine Vibes",
            ("casual", "clouds"): "Cozy Urban Explorer", 
            ("casual", "rain"): "Chic Storm Chaser",
            ("casual", "snow"): "Winter Wonderland Wanderer",
            ("formal", "clear"): "Polished Perfection",
            ("formal", "clouds"): "Sophisticated City Dweller",
            ("formal", "rain"): "Executive Weather Warrior", 
            ("formal", "snow"): "Elegant Winter Professional",
            ("sporty", "clear"): "Athletic Sunshine Ready",
            ("sporty", "clouds"): "Urban Athlete Meets Cool Breeze",
            ("sporty", "rain"): "Storm-Proof Fitness Champion",
            ("sporty", "snow"): "Winter Sports Enthusiast"
        }
        
        # Create weather condition description
        weather_descriptions = {
            "clear": "Bright & Beautiful",
            "clear sky": "Bright & Beautiful",
            "few clouds": "Partly Cloudy & Pleasant", 
            "scattered clouds": "Cloudy with Character",
            "broken clouds": "Dramatically Overcast",
            "overcast clouds": "Moody & Atmospheric",
            "light rain": "Gentle Drizzle",
            "moderate rain": "Refreshing Rainfall", 
            "heavy rain": "Intense Downpour",
            "light snow": "Delicate Snowfall",
            "snow": "Winter Wonderland",
            "mist": "Mysterious & Misty",
            "fog": "Dreamy & Ethereal"
        }
        
        # Determine weather description
        weather_desc = weather_descriptions.get(conditions.lower(), conditions.title())
        if wind_speed and wind_speed != "unknown" and float(wind_speed) > 15:
            weather_desc += " & Breezy" if float(wind_speed) < 25 else " & Windy"
        if temp != "unknown" and float(temp) <= 10:
            weather_desc += " & Cool" if float(temp) > 5 else " & Cold"
        elif temp != "unknown" and float(temp) >= 25:
            weather_desc += " & Warm" if float(temp) < 30 else " & Hot"
            
        # Get mood tag
        style_lower = style_preference.lower()
        condition_key = None
        for key_condition in ["clear", "cloud", "rain", "snow", "mist", "fog"]:
            if key_condition in conditions.lower():
                condition_key = key_condition
                break
        if not condition_key:
            condition_key = "clear"
            
        mood_tag = mood_tags.get((style_lower, condition_key), f"{style_preference.title()} & Weather-Ready")
        
        # Create beautiful header with proper spacing
        header_top = f"\n{Fore.CYAN}{'═' * 60}"
        header_title = f"{Fore.CYAN}👗  WEATHERWEAR STYLE RECOMMENDATION"
        header_separator = f"{Fore.CYAN}{'═' * 60}{Style.RESET_ALL}"
        
        # Create organized recommendation info box
        rec_info = f"""
{Fore.WHITE}┌─ Location & Style ───────────────────────────────────────┐
{Fore.WHITE}│ 🏙️  {Fore.YELLOW}{weather_location}, {country}{Style.RESET_ALL}{Fore.WHITE}                                        │
{Fore.WHITE}│ 👟  Style: {Fore.MAGENTA}{style_preference.title()} & Stylish{Style.RESET_ALL}{Fore.WHITE}                            │
{Fore.WHITE}│ 🌬️  Conditions: {Fore.GREEN}{weather_desc}{Style.RESET_ALL}{Fore.WHITE}                           │
{Fore.WHITE}│ 💡  Mood: "{Fore.CYAN}{mood_tag}{Style.RESET_ALL}{Fore.WHITE}"                         │
{Fore.WHITE}└──────────────────────────────────────────────────────────┘{Style.RESET_ALL}
"""
        
        # Format the recommendation content with better spacing
        formatted_content = self._add_proper_spacing_to_recommendation(recommendation)
        
        # Create beautiful footer
        footer = f"\n{Fore.CYAN}{'═' * 60}{Style.RESET_ALL}\n"
        
        return f"{header_top}\n{header_title}\n{header_separator}{rec_info}\n{formatted_content}{footer}"
    
    def _add_proper_spacing_to_recommendation(self, recommendation: str) -> str:
        """Add proper spacing and formatting to the recommendation content."""
        lines = recommendation.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Add extra spacing around major sections
            if line.startswith('🎽'):
                formatted_lines.append(f"\n{Fore.YELLOW}{line}{Style.RESET_ALL}")
                formatted_lines.append("")
            elif line.startswith(('🧢', '👕', '👖', '👟', '🧤')):
                formatted_lines.append(f"{Fore.WHITE}{line}{Style.RESET_ALL}")
            elif line.startswith('🧠'):
                formatted_lines.append(f"\n{Fore.CYAN}{line}{Style.RESET_ALL}")
            elif line.startswith('🌍'):
                formatted_lines.append(f"\n{Fore.GREEN}{line}{Style.RESET_ALL}")
            elif line.startswith('🎒'):
                formatted_lines.append(f"\n{Fore.BLUE}{line}{Style.RESET_ALL}")
            elif line.startswith('🎵'):
                formatted_lines.append(f"\n{Fore.MAGENTA}{line}{Style.RESET_ALL}")
            elif line.startswith('💬'):
                formatted_lines.append(f"\n{Fore.YELLOW}{line}{Style.RESET_ALL}")
            elif line.startswith('🗣️'):
                formatted_lines.append(f"{Fore.GREEN}{line}{Style.RESET_ALL}")
            elif line.startswith(('🧴', '🔋', '🧦', '🧃', '🧼', '🌂', '🕶️')):
                formatted_lines.append(f"  {Fore.WHITE}{line}{Style.RESET_ALL}")
            else:
                # Regular content lines
                if line.strip():
                    formatted_lines.append(f"{line}")
        
        return '\n'.join(formatted_lines)