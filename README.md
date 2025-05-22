# WeatherWear

WeatherWear: Your AI-Powered Outfit Recommender
WeatherWear is an intelligent Flask web application that provides personalized outfit recommendations based on real-time and forecasted weather, leveraging natural language understanding and a powerful AI.

✨ **Key Features**
Smart Recommendations: AI-powered outfit suggestions based on current or future weather.

Natural Language Input: Understands queries like "Tokyo tomorrow" or "here."

Comprehensive Weather: Fetches current conditions and 5-day forecasts from OpenWeatherMap.

Personalized Style: Tailors recommendations to user-selected styles (Casual, Formal, Sporty, etc.).

Detailed Insights: Includes layering tips, local fashion, and packing lists.

User-Friendly Interface: Clean, responsive web UI.

🚀 **Technologies Used**
Backend: Python 3, Flask, requests, python-dotenv, groq (Mixtral-8x7B), colorama, pytz.

Frontend: HTML5, CSS3, JavaScript, Font Awesome.

⚙️ **Setup and Installation**
Clone the repository: git clone https://github.com/your-username/WeatherWear.git

**Set up virtual environment & install dependencies:**

python -m venv venv
# Activate venv (Windows: .\venv\Scripts\activate | Linux/macOS: source venv/bin/activate)
pip install Flask requests python-dotenv groq colorama pytz

Obtain API Keys: Get keys from OpenWeatherMap and Groq Console.

Configure .env: Create .env in the root with OPENWEATHER_API_KEY="your_key" and GROQ_API_KEY="your_key". (Add proxy settings if needed).

🚀** Usage**
Run the app: python app_web.py

Open in browser: Navigate to http://localhost:5000.

Enter query: Type location and time (e.g., "New York", "Tomorrow evening in Paris").

Select style: Choose your preferred style.

Get Recommendation: Click the button to see your personalized outfit.

📂 Project Structure
WeatherWear/
├── app_web.py
├── .env
├── templates/
│   └── index.html
└── src/
    ├── outfit_generator.py
    ├── weather_api.py
    ├── llm_api.py
    └── utils.py

💡 Future Enhancements
More advanced Natural Language Processing (NLP).

User authentication & profiles.

Visual outfit generation.

Expanded style options.

Mobile application development.

📄 License
This project is open-source and available under the MIT License.
