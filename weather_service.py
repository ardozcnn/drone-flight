from http_client import http_get

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

CURRENT_VARS = ",".join([
    "temperature_2m",
    "apparent_temperature",
    "relative_humidity_2m",
    "precipitation",
    "rain",
    "weather_code",
    "cloud_cover",
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
    "surface_pressure",
    "is_day",
])

HOURLY_VARS = ",".join([
    "temperature_2m",
    "wind_speed_10m",
    "wind_gusts_10m",
    "precipitation_probability",
    "weather_code",
])


def fetch_weather(latitude: float, longitude: float) -> dict:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": CURRENT_VARS,
        "hourly": HOURLY_VARS,
        "forecast_hours": 12,
        "wind_speed_unit": "kmh",
        "timezone": "auto",
    }

    response = http_get(OPEN_METEO_URL, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def reverse_geocode(latitude: float, longitude: float) -> str:
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "json",
            "accept-language": "tr",
        }
        headers = {"User-Agent": "DroneFlightSafety/1.0"}
        resp = http_get(url, params=params, headers=headers, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        address = data.get("address", {})
        city = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("county")
            or address.get("state")
        )
        country = address.get("country", "")
        if city and country:
            return f"{city}, {country}"
        return data.get("display_name", f"{latitude:.4f}, {longitude:.4f}")
    except Exception:
        return f"{latitude:.4f}°N, {longitude:.4f}°E"
