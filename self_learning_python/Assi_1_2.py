

import argparse
import sys
from datetime import datetime

import requests

API_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT_SECONDS = 10
LOG_FILE = "weather_report.txt"

# Default coordinates (New Delhi) used when none are given
DEFAULT_LAT = 28.6139
DEFAULT_LON = 77.2090

# WMO weather interpretation codes used by Open-Meteo
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def fetch_weather(lat, lon):
    """
    Send a GET request to Open-Meteo and return the decoded JSON (a dict).
    Raises RuntimeError with a  message if anything goes wrong.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "timezone": "auto",       # makes the API include the local timezone name
    }

    try:
        response = requests.get(API_URL, params=params, timeout=TIMEOUT_SECONDS)

        # Treat anything other than 200 OK as a failure
        if response.status_code != 200:
            raise RuntimeError(
                f"API returned HTTP {response.status_code}: {response.reason}. "
                "Check the latitude/longitude values and try again."
            )

        return response.json()    # may raise ValueError if the body is not JSON

    except requests.exceptions.Timeout:
        raise RuntimeError(
            f"The request timed out after {TIMEOUT_SECONDS} seconds. "
            "The server is slow or unreachable; try again later."
        )
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Could not connect to the weather service. Check your internet connection."
        )
    except requests.exceptions.RequestException as err:
        # Catch-all for any other requests problem (invalid URL, too many redirects...)
        raise RuntimeError(f"Network error while contacting the API: {err}")
    except ValueError:
        raise RuntimeError("The server's response was not valid JSON.")



def parse_weather(data):
    """Pull temperature, windspeed, weathercode and timezone out of the JSON."""
    try:
        current = data["current_weather"]
        return {
            "temperature": current["temperature"],
            "windspeed": current["windspeed"],
            "weathercode": current["weathercode"],
            "timezone": data["timezone"],
            "observed_at": current.get("time", "unknown"),
        }
    except (KeyError, TypeError):
        # The API sends {"error": true, "reason": "..."} for bad requests
        reason = data.get("reason") if isinstance(data, dict) else None
        raise RuntimeError(
            "The response did not contain the expected weather fields"
            + (f" ({reason})." if reason else ".")
        )



def format_summary(metrics, lat, lon):
    """Turn the metrics dictionary into a human-readable text block."""
    condition = WEATHER_CODES.get(metrics["weathercode"], "Unknown conditions")
    return (
        f"Weather report for ({lat}, {lon})\n"
        f"  Observed at : {metrics['observed_at']}\n"
        f"  Timezone    : {metrics['timezone']}\n"
        f"  Temperature : {metrics['temperature']} °C\n"
        f"  Wind speed  : {metrics['windspeed']} km/h\n"
        f"  Conditions  : {condition} (code {metrics['weathercode']})\n"
    )


def save_report(summary, path=LOG_FILE):
    """Append the summary, with a timestamp, to the log file."""
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(path, "a", encoding="utf-8") as log:
            log.write(f"=== Logged {stamp} ===\n{summary}\n")
    except OSError as err:
        raise RuntimeError(f"Could not write to {path}: {err}")


#entry point
def main():
    parser = argparse.ArgumentParser(description="Fetch current weather from Open-Meteo.")
    parser.add_argument("--lat", type=float, default=DEFAULT_LAT, help="latitude (-90 to 90)")
    parser.add_argument("--lon", type=float, default=DEFAULT_LON, help="longitude (-180 to 180)")
    args = parser.parse_args()

    try:
        data = fetch_weather(args.lat, args.lon)
        metrics = parse_weather(data)
        summary = format_summary(metrics, args.lat, args.lon)
        save_report(summary)
    except RuntimeError as err:
        print(f"Error: {err}")
        sys.exit(1)

    print(summary)
    print(f"Saved to {LOG_FILE}")


if __name__ == "__main__":
    main()