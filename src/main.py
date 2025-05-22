#!/usr/bin/env python3
"""
WeatherWear: Weather-Based Outfit Recommender
Main entry point for the application.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from colorama import Fore, Style, init
import traceback

# Load environment variables from .env file
load_dotenv()

# Add project root to path to ensure imports work
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Initialize colorama for cross-platform colored terminal output
init(autoreset=True)

from src.outfit_generator import OutfitGenerator
from src.utils import validate_style_preference

def print_welcome():
    """Display welcome message."""
    print(f"\n{Fore.CYAN}===== WeatherWear: Weather-Based Outfit Recommender ====={Style.RESET_ALL}")
    print(f"{Fore.CYAN}Get smart outfit recommendations based on weather conditions{Style.RESET_ALL}\n")

def print_instructions():
    """Display usage instructions."""
    print(f"{Fore.YELLOW}Enter a location and optional time{Style.RESET_ALL}")
    print("Examples:")
    print("  - New York")
    print("  - Tomorrow in London")
    # print("  - Paris evening")
    print("  - Tokyo tomorrow")
    print("  - here (uses your current location)")
    print("  - my location (uses your current location)\n")

def get_user_input() -> tuple:
    """Get location query and style preference from user."""
    location_query = input(f"{Fore.GREEN}Enter location: {Style.RESET_ALL}")
    style_prompt = f"{Fore.GREEN}Enter style preference (casual/formal/sporty): {Style.RESET_ALL}"
    style_input = input(style_prompt)
    
    # Ask if user wants to see the 5-day forecast
    forecast_prompt = f"{Fore.GREEN}Show 5-day forecast? (y/n) [n]: {Style.RESET_ALL}"
    forecast_input = input(forecast_prompt).lower().strip()
    show_forecast = forecast_input in ['y', 'yes', 'true']
    
    # Default to casual if no style is provided
    style_preference = validate_style_preference(style_input)
    
    return location_query, style_preference, show_forecast

def main():
    """Main entry point for WeatherWear application."""
    print_welcome()
    print_instructions()
    
    try:
        # Get user input
        location_query, style_preference, show_forecast = get_user_input()
        
        print(f"\n{Fore.CYAN}Fetching weather data and generating outfit recommendation...{Style.RESET_ALL}")
        
        # Create outfit generator
        outfit_generator = OutfitGenerator()
        
        # Process query and get recommendation
        weather_info, outfit_recommendation, forecast_info = outfit_generator.process_query(
            query=location_query,
            style_preference=style_preference,
            show_forecast=show_forecast
        )
        
        # Display results
        print("\n" + weather_info)
        print(outfit_recommendation)
        
        # Show forecast if requested
        if show_forecast and forecast_info:
            print(forecast_info)
        
    except ValueError as e:
        print(f"\n{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}An unexpected error occurred: {str(e)}{Style.RESET_ALL}")
    traceback.print_exc()


if __name__ == "__main__":
    main()