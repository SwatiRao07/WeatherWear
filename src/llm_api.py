import os
from typing import Dict, Any, Optional
import groq
from .utils import load_env_variable

class LLMClient:
    """
    Handles interactions with the Groq LLM API.
    """
    
    def __init__(self):
        """Initialize the LLM client with API key from environment variables."""
        self.api_key = load_env_variable("GROQ_API_KEY")
        self.model = load_env_variable("GROQ_MODEL", "llama-3.1-70b-versatile")
        
        # Set environment variable first
        os.environ["GROQ_API_KEY"] = self.api_key
        
        # Try different initialization methods with more specific error handling
        self.client = None
        
        # Method 1: Try with explicit API key (most common)
        try:
            self.client = groq.Groq(api_key=self.api_key)
            print("Groq client initialized successfully with API key")
        except Exception as e:
            print(f"Method 1 failed: {e}")
            
            # Method 2: Try without explicit API key (uses environment)
            try:
                self.client = groq.Groq()
                print("Groq client initialized successfully from environment")
            except Exception as e2:
                print(f"Method 2 failed: {e2}")
                
                # Method 3: Try importing differently
                try:
                    from groq import Groq
                    self.client = Groq(api_key=self.api_key)
                    print("Groq client initialized with direct import")
                except Exception as e3:
                    print(f"Method 3 failed: {e3}")
                    
                    # Method 4: Last resort - create a mock client for testing
                    print("All Groq initialization methods failed. Using fallback mode.")
                    self.client = None
        
    def generate_outfit_recommendation(
        self, 
        weather_data: Dict[str, Any], 
        location: str, 
        style_preference: str,
        is_future: bool
    ) -> str:
        """
        Generate outfit recommendations based on weather data.
        
        Args:
            weather_data: Weather data from OpenWeatherMap API
            location: Location name
            style_preference: User's style preference (casual, formal, sporty)
            is_future: Whether the weather data is for future or current
            
        Returns:
            Outfit recommendation text
        """
        # Extract relevant weather information
        try:
            temp = weather_data.get("main", {}).get("temp", "unknown")
            feels_like = weather_data.get("main", {}).get("feels_like", "unknown")
            humidity = weather_data.get("main", {}).get("humidity", "unknown")
            wind_speed = weather_data.get("wind", {}).get("speed", "unknown")
            conditions = weather_data.get("weather", [{}])[0].get("description", "unknown") if weather_data.get("weather") else "unknown"
            weather_location = weather_data.get("name", location)
            country = weather_data.get("sys", {}).get("country", "")
            
            # Format time context
            time_context = "current" if not is_future else "forecasted"
            
            # Create enhanced prompt for detailed recommendations
            prompt = f"""
            You are WeatherWear, an expert fashion stylist who creates detailed, creative, and personalized outfit recommendations. 
            Create a comprehensive outfit recommendation for {weather_location}, {country} with the following weather:
            - Temperature: {temp}°C (feels like {feels_like}°C)
            - Humidity: {humidity}%
            - Wind: {wind_speed} km/h
            - Conditions: {conditions}
            - Style: {style_preference}
            - Time context: {time_context}
            
            Structure your response EXACTLY like this format with emojis and sections:
            
            🎽 Your Look, Tailored to [Weather Description] & [Location Vibe]
            [Weather mood description]: [Creative description of conditions]
            
            [Detailed clothing recommendations organized by category:]
            🧢 Top Layer: [Specific item with creative description]
            👕 Mid-Layer: [Specific item with style notes]
            👖 Bottoms: [Specific item with practical benefits]
            👟 Shoes: [Specific footwear with weather considerations]
            🧤 Accessories: [1-2 key accessories with style reasoning]
            
            🧠 Smart Layering Tip:
            [Professional styling advice specific to the weather and style]
            
            🌍 Local Flavor Add-On:
            [Cultural or location-specific styling suggestion that locals would wear]
            
            🎒 Your Pack & Prep List:
            [5-6 practical items with emojis, each on a new line starting with emoji]
            
            🎵 [Creative playlist name related to weather/location] 🎧
            
            💬 Confidence Closer:
            [Motivational closing that ties together the weather, location, and style preference. Should be 2-3 sentences ending with a confident quote.]
            
            Make it creative, detailed, and weather-appropriate for {style_preference} style. Use vivid descriptions and practical advice.
            """
            
            # Generate recommendation using Groq API
            if self.client is not None:
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    model=self.model,
                    temperature=0.8,
                    max_tokens=800,
                    top_p=0.9
                )
                
                # Extract the generated text
                recommendation = chat_completion.choices[0].message.content
                return recommendation.strip()
            else:
                # Use fallback if client initialization failed
                return self._create_fallback_recommendation(weather_data, location, style_preference, "Groq client not available")
            
        except Exception as e:
            # Fallback recommendation if there's an error
            return self._create_fallback_recommendation(weather_data, location, style_preference, str(e))
    
    def _create_fallback_recommendation(self, weather_data: Dict[str, Any], location: str, style_preference: str, error: str = "") -> str:
        """Create a detailed, weather-specific fallback recommendation if LLM fails."""
        temp = weather_data.get("main", {}).get("temp", 20)
        feels_like = weather_data.get("main", {}).get("feels_like", temp)
        humidity = weather_data.get("main", {}).get("humidity", 50)
        wind_speed = weather_data.get("wind", {}).get("speed", 0)
        conditions = weather_data.get("weather", [{}])[0].get("description", "clear") if weather_data.get("weather") else "clear"
        weather_location = weather_data.get("name", location)
        country = weather_data.get("sys", {}).get("country", "")
        
        # Determine clothing based on temperature
        if temp >= 30:
            temp_category = "hot"
            top_layer = "Light cotton shirt or breathable tank top"
            mid_layer = "Skip the mid-layer - keep it minimal"
            bottoms = "Lightweight shorts or linen pants"
            shoes = "Breathable sneakers or sandals"
        elif temp >= 25:
            temp_category = "warm"
            top_layer = "Cotton t-shirt or light blouse"
            mid_layer = "Light cardigan or kimono (optional)"
            bottoms = "Comfortable chinos or light jeans"
            shoes = "Canvas sneakers or loafers"
        elif temp >= 20:
            temp_category = "mild"
            top_layer = "Long-sleeve shirt or light sweater"
            mid_layer = "Denim jacket or light hoodie"
            bottoms = "Jeans or comfortable trousers"
            shoes = "Sneakers or casual boots"
        elif temp >= 15:
            temp_category = "cool"
            top_layer = "Warm sweater or fleece"
            mid_layer = "Light jacket or blazer"
            bottoms = "Warm pants or dark jeans"
            shoes = "Closed-toe shoes or ankle boots"
        else:
            temp_category = "cold"
            top_layer = "Warm coat or heavy jacket"
            mid_layer = "Thick sweater or hoodie"
            bottoms = "Warm pants with thermal layer"
            shoes = "Insulated boots or warm shoes"
            
        # Adjust for style preference
        if style_preference.lower() == "formal":
            if temp >= 25:
                top_layer = "Lightweight dress shirt or silk blouse"
                bottoms = "Dress pants or midi skirt"
                shoes = "Leather loafers or heeled sandals"
            else:
                top_layer = "Button-down shirt or tailored blouse"
                mid_layer = "Blazer or structured cardigan"
                bottoms = "Dress pants or pencil skirt"
                shoes = "Oxford shoes or low heels"
        elif style_preference.lower() == "sporty":
            if temp >= 25:
                top_layer = "Moisture-wicking athletic top"
                bottoms = "Athletic shorts or leggings"
                shoes = "Running shoes or training sneakers"
            else:
                top_layer = "Athletic long-sleeve or hoodie"
                bottoms = "Track pants or athletic leggings"
                shoes = "Cross-training shoes or athletic sneakers"
                
        # Weather-specific adjustments
        accessories = []
        weather_adjustments = ""
        
        if "rain" in conditions.lower():
            accessories.extend(["Waterproof jacket or umbrella", "Water-resistant shoes"])
            weather_adjustments = "The rain calls for waterproof layers and quick-dry materials."
        elif "snow" in conditions.lower():
            accessories.extend(["Warm hat and gloves", "Waterproof boots"])
            weather_adjustments = "Snow means insulation is key - layer up and stay dry."
        elif wind_speed > 15:
            accessories.append("Windbreaker or scarf")
            weather_adjustments = f"With {wind_speed} km/h winds, wind-resistant layers will keep you comfortable."
        elif humidity > 70:
            weather_adjustments = f"High humidity ({humidity}%) means breathable, moisture-wicking fabrics are your friend."
        elif "haze" in conditions.lower() or "fog" in conditions.lower():
            weather_adjustments = "Hazy conditions mean the air might feel thick - opt for breathable layers."
        else:
            weather_adjustments = f"Perfect {conditions} weather - dress comfortably for the temperature."
            
        if not accessories:
            accessories = ["Sunglasses for UV protection", "Light scarf (versatile for style or warmth)"]
            
        # Location-specific suggestions
        location_tips = {
            "mumbai": "Mumbai's coastal humidity calls for cotton and linen - avoid synthetic fabrics!",
            "delhi": "Delhi's dry climate is perfect for layering - add a light jacket for evening temperature drops.",
            "bangalore": "Bangalore's pleasant weather is ideal for smart-casual looks with light layers.",
            "chennai": "Chennai's heat and humidity require maximum breathability - cotton is king!",
            "kolkata": "Kolkata's cultural vibe pairs well with comfortable yet stylish ethnic-western fusion.",
            "hyderabad": "Hyderabad's moderate climate allows for versatile styling - perfect for experimenting!",
            "pune": "Pune's weather is ideal for outdoor activities - dress comfortably for movement.",
            "nagpur": "Nagpur's central location means variable weather - layering is your best strategy!"
        }
        
        location_tip = location_tips.get(weather_location.lower(), f"Local {weather_location} style embraces comfort with a touch of regional flair!")
        
        # Create playlist based on weather and location
        playlist_names = {
            "hot": "Tropical Chill Vibes",
            "warm": "Sunny Day Grooves", 
            "mild": "Perfect Weather Playlist",
            "cool": "Cozy Comfort Tunes",
            "cold": "Winter Warmth Beats"
        }
        
        playlist = playlist_names.get(temp_category, "Weather Perfect Playlist")
        
        return f"""🎽 Your Look, Tailored to {conditions.title()} & {weather_location} Vibes
{weather_adjustments} At {temp}°C (feels like {feels_like}°C), comfort meets style effortlessly.

🧢 Top Layer: {top_layer}
👕 Mid-Layer: {mid_layer}
👖 Bottoms: {bottoms}
👟 Shoes: {shoes}
🧤 Accessories: {' and '.join(accessories)}

🧠 Smart Layering Tip:
With {temp}°C weather and {humidity}% humidity, focus on breathable materials that can adapt as temperatures change throughout the day. {'' if temp >= 25 else 'Light layers you can add or remove are key for comfort.'}

🌍 Local Flavor Add-On:
{location_tip}

🎒 Your Pack & Prep List:
🧴 {'Sunscreen SPF 30+' if temp >= 25 else 'Light moisturizer'}
🔋 Portable phone charger
🧦 {'Moisture-wicking socks' if temp >= 25 else 'Comfortable cotton socks'}
🧃 {'Insulated water bottle - stay hydrated!' if temp >= 25 else 'Warm drink in a thermos'}
🧼 {'Cooling face wipes' if temp >= 25 else 'Hand sanitizer and tissues'}
{'🌂 Compact umbrella' if 'rain' in conditions.lower() else '🕶️ Sunglasses for eye protection'}

🎵 {playlist} 🎧

💬 Confidence Closer:
Perfect weather calls for perfect style! You're dressed to embrace {weather_location}'s {temp}°C {conditions} with confidence and comfort. Whether you're exploring the city or enjoying a casual day out, your look says effortless sophistication.
🗣️ "Weather-ready and style-perfect - bring on the day!"

{f"Have a Great Day!" if error else ""}"""