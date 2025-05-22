#!/usr/bin/env python3
"""
WeatherWear Flask Web Application
Run this to access WeatherWear via web browser at http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import traceback
import re

from colorama import init # Ensure this import is here

# Initialize Colorama for proper ANSI code handling across the application.
# This must be called early to ensure colorama translates its constants
# into actual ANSI escape sequences (e.g., \x1b[36m) for all output.
init()

# Load environment variables from .env file
load_dotenv()

# Add project root to path to allow importing modules from src/
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Import your existing modules
from src.outfit_generator import OutfitGenerator
from src.utils import validate_style_preference

app = Flask(__name__)

def convert_ansi_to_html(text):
    """
    Convert ANSI color codes to HTML with CSS classes.
    This function is made more robust to handle both standard ANSI codes
    and the literal "[ XXm" patterns observed in some environments.
    """
    ansi_patterns = {
        # Reset codes - these should generally be processed first or last
        # depending on if they are part of a longer sequence.
        # Placing them here to ensure they close spans.
        r'\x1b\[0m': '</span>',                       # Reset all attributes
        r'\x1b\[39m': '</span>',                      # Reset foreground color
        r'\x1b\[49m': '</span>',                      # Reset background color

        # Standard Foreground Colors (30-37)
        r'\x1b\[30m': '<span class="text-black">',
        r'\x1b\[31m': '<span class="text-red">',
        r'\x1b\[32m': '<span class="text-green">',
        r'\x1b\[33m': '<span class="text-yellow">',
        r'\x1b\[34m': '<span class="text-blue">',
        r'\x1b\[35m': '<span class="text-magenta">',
        r'\x1b\[36m': '<span class="text-cyan">',
        r'\x1b\[37m': '<span class="text-white">',

        # Bright Foreground Colors (90-97)
        r'\x1b\[90m': '<span class="text-gray">', # Typically bright black/dark gray
        r'\x1b\[91m': '<span class="text-bright-red">',
        r'\x1b\[92m': '<span class="text-bright-green">',
        r'\x1b\[93m': '<span class="text-bright-yellow">',
        r'\x1b\[94m': '<span class="text-bright-blue">',
        r'\x1b\[95m': '<span class="text-bright-magenta">',
        r'\x1b\[96m': '<span class="text-bright-cyan">',
        r'\x1b\[97m': '<span class="text-bright-white">',

        # Fallback patterns for literal "[ XXm" (with optional space)
        # These are added to catch cases where \x1b is missing and a space is present.
        # They should be processed *after* the \x1b patterns to prioritize correct ones.
        r'\[\s*0m': '</span>',
        r'\[\s*39m': '</span>',
        r'\[\s*49m': '</span>',

        r'\[\s*30m': '<span class="text-black">',
        r'\[\s*31m': '<span class="text-red">',
        r'\[\s*32m': '<span class="text-green">',
        r'\[\s*33m': '<span class="text-yellow">',
        r'\[\s*34m': '<span class="text-blue">',
        r'\[\s*35m': '<span class="text-magenta">',
        r'\[\s*36m': '<span class="text-cyan">',
        r'\[\s*37m': '<span class="text-white">',

        r'\[\s*90m': '<span class="text-gray">',
        r'\[\s*91m': '<span class="text-bright-red">',
        r'\[\s*92m': '<span class="text-bright-green">',
        r'\[\s*93m': '<span class="text-bright-yellow">',
        r'\[\s*94m': '<span class="text-bright-blue">',
        r'\[\s*95m': '<span class="text-bright-magenta">',
        r'\[\s*96m': '<span class="text-bright-cyan">',
        r'\[\s*97m': '<span class="text-bright-white">',
    }
    
    # Sort patterns by length in descending order to prevent partial matches
    # (e.g., ensure r'\x1b[91m' is matched before r'\x1b[1m' if both were present and overlapping)
    # This is good practice for regex replacement order.
    sorted_patterns = sorted(ansi_patterns.items(), key=lambda item: len(item[0]), reverse=True)

    for pattern, replacement in sorted_patterns:
        text = re.sub(pattern, replacement, text)
    
    # Convert newlines to HTML breaks for proper rendering in browser
    text = text.replace('\n', '<br>')
    
    # Convert multiple spaces to non-breaking spaces for formatting
    # This helps preserve the layout from terminal output in HTML.
    # It replaces sequences of 2 or more spaces with equivalent &nbsp;
    text = re.sub(r' {2,}', lambda m: '&nbsp;' * len(m.group()), text)
    
    return text

def format_for_web(text):
    """
    Format the terminal output for web display.
    This function first converts ANSI codes to HTML, then handles box drawing characters.
    """
    # Convert ANSI codes to HTML spans
    html_text = convert_ansi_to_html(text)
    
    # Replace box drawing characters with HTML equivalents.
    # These are usually rendered correctly by modern browsers, but explicit
    # replacement can ensure consistency if font support is an issue.
    # For now, keeping them as is, assuming font support is adequate.
    replacements = {
        '═': '═',
        '─': '─', 
        '┌': '┌',
        '┐': '┐',
        '└': '└',
        '┘': '┘',
        '│': '│',
    }
    
    for old, new in replacements.items():
        html_text = html_text.replace(old, new)
    
    return html_text

@app.route('/')
def index():
    """Main page with the input form."""
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def get_recommendation():
    """Process the recommendation request."""
    try:
        # Get form data from the incoming request
        location_query = request.form.get('location', '').strip()
        style_preference = request.form.get('style', 'casual').strip()
        show_forecast = request.form.get('forecast') == 'on'
        
        # Validate that a location query was provided
        if not location_query:
            return jsonify({
                'error': 'Please enter a location.',
                'success': False
            })
        
        # Validate and normalize the style preference
        style_preference = validate_style_preference(style_preference)
        
        # Create an instance of OutfitGenerator and process the user's query
        outfit_generator = OutfitGenerator()
        weather_info, outfit_recommendation, forecast_info = outfit_generator.process_query(
            query=location_query,
            style_preference=style_preference,
            show_forecast=show_forecast
        )
        
        # Format the retrieved data for display in the web browser
        weather_html = format_for_web(weather_info)
        outfit_html = format_for_web(outfit_recommendation)
        forecast_html = format_for_web(forecast_info) if forecast_info else ""
        
        # Return the formatted data as a JSON response
        return jsonify({
            'success': True,
            'weather': weather_html,
            'outfit': outfit_html,
            'forecast': forecast_html,
            'location': location_query,
            'style': style_preference.title()
        })
        
    except ValueError as e:
        # Handle specific validation errors
        return jsonify({
            'error': str(e),
            'success': False
        })
    except Exception as e:
        # Catch any other unexpected errors and provide a generic message
        # traceback.format_exc() can be used here for more detailed logging in debug mode
        return jsonify({
            'error': f'An unexpected error occurred: {str(e)}',
            'success': False
        })

if __name__ == '__main__':
    # Ensure the 'templates' directory exists for Flask to find HTML files
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)
    
    print("🌐 Starting WeatherWear Web Server...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    
    # Run the Flask application. debug=True enables reloader and debugger.
    app.run(debug=True, host='localhost', port=5000)

