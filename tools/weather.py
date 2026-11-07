import requests
from langchain_core.tools import tool
from settings import DEFAULT_CITY


@tool
def get_weather(city: str = "") -> str:
    """Get current weather for a city."""

    city = city.strip() or DEFAULT_CITY

    if not city:
        return "Please provide a city name."

    try:
        url = f"https://wttr.in/{city}"

        response = requests.get(
            url,
            params={"format": "j1"},
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        current = data["current_condition"][0]
        today = data["weather"][0]

        return (
            f"Weather in {city}:\n"
            f"Temperature: {current['temp_C']}°C\n"
            f"Feels like: {current['FeelsLikeC']}°C\n"
            f"Condition: {current['weatherDesc'][0]['value']}\n"
            f"Humidity: {current['humidity']}%\n"
            f"Wind: {current['windspeedKmph']} km/h\n"
            f"Today's High: {today['maxtempC']}°C\n"
            f"Today's Low: {today['mintempC']}°C"
        )

    except Exception as e:
        return f"Weather error: {e}"


WEATHER_TOOLS = [get_weather]