from flask import Flask, render_template, request, jsonify

from weather_service import fetch_weather, reverse_geocode
from flight_analyzer import (
    DRONE_PRESETS,
    FlightLimits,
    analyze_flight,
    analysis_to_dict,
)

app = Flask(__name__)

DEFAULT_LAT = 41.0082
DEFAULT_LON = 28.9784


@app.route("/")
def index():
    presets = {
        key: {
            "name": lim.name,
            "max_wind_kmh": lim.max_wind_kmh,
            "max_gust_kmh": lim.max_gust_kmh,
            "max_precip_mm": lim.max_precip_mm,
            "max_cloud_cover": lim.max_cloud_cover,
            "min_temp_c": lim.min_temp_c,
            "max_temp_c": lim.max_temp_c,
            "max_rain_probability": lim.max_rain_probability,
        }
        for key, lim in DRONE_PRESETS.items()
    }
    return render_template(
        "index.html",
        default_lat=DEFAULT_LAT,
        default_lon=DEFAULT_LON,
        presets=presets,
    )


@app.route("/api/analyze", methods=["GET"])
def api_analyze():
    try:
        lat = float(request.args.get("lat", DEFAULT_LAT))
        lon = float(request.args.get("lon", DEFAULT_LON))
    except (TypeError, ValueError):
        return jsonify({"error": "Geçersiz koordinat"}), 400

    preset_key = request.args.get("preset", "dji_mavic")
    limits = DRONE_PRESETS.get(preset_key, DRONE_PRESETS["dji_mavic"])

    if preset_key == "custom" or request.args.get("custom") == "1":
        try:
            limits = FlightLimits(
                name="Özel Limitler",
                max_wind_kmh=float(request.args.get("max_wind", limits.max_wind_kmh)),
                max_gust_kmh=float(request.args.get("max_gust", limits.max_gust_kmh)),
                max_precip_mm=float(request.args.get("max_precip", limits.max_precip_mm)),
                max_cloud_cover=float(request.args.get("max_cloud", limits.max_cloud_cover)),
                min_temp_c=float(request.args.get("min_temp", limits.min_temp_c)),
                max_temp_c=float(request.args.get("max_temp", limits.max_temp_c)),
                max_rain_probability=float(
                    request.args.get("max_rain_prob", limits.max_rain_probability)
                ),
            )
        except (TypeError, ValueError):
            return jsonify({"error": "Geçersiz limit değerleri"}), 400

    try:
        weather = fetch_weather(lat, lon)
    except Exception as exc:
        return jsonify({"error": f"Hava verisi alınamadı: {exc}"}), 502

    analysis = analyze_flight(weather, limits)
    location_name = reverse_geocode(lat, lon)

    current = weather.get("current", {})
    hourly = weather.get("hourly", {})

    return jsonify({
        "location": {"lat": lat, "lon": lon, "name": location_name},
        "current": current,
        "hourly": {
            "time": hourly.get("time", [])[:12],
            "wind_speed_10m": hourly.get("wind_speed_10m", [])[:12],
            "wind_gusts_10m": hourly.get("wind_gusts_10m", [])[:12],
            "precipitation_probability": hourly.get("precipitation_probability", [])[:12],
        },
        "analysis": analysis_to_dict(analysis),
        "limits": {
            "name": limits.name,
            "max_wind_kmh": limits.max_wind_kmh,
            "max_gust_kmh": limits.max_gust_kmh,
        },
        "timezone": weather.get("timezone", "UTC"),
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
