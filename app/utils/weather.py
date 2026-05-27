import requests
import os
import time
from datetime import datetime
from app.config import Config


_cache = {}


def get_weather_data(location: str) -> dict:
    """
    Fetch live weather data from OpenWeatherMap.
    Results are cached for 1 hour to respect free tier rate limits.
    """
    now = time.time()

    # Return cached result if still fresh
    if location in _cache:
        cached_data, timestamp = _cache[location]
        if now - timestamp < Config.CACHE_TTL_SECONDS:
            cached_data["cache_hit"] = True
            return cached_data

    # Fetch fresh data from API
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location,
        "appid": Config.OPENWEATHER_API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params, timeout=5)
    response.raise_for_status()
    data = response.json()

    result = {
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "rainfall": data.get("rain", {}).get("1h", 0),
        "weather_description": data["weather"][0]["description"],
        "timestamp": datetime.utcnow().isoformat(),
        "cache_hit": False
    }

    # Store in cache
    _cache[location] = (result, now)
    return result