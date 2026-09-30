from flask import Flask, jsonify, send_from_directory
import requests
import csv
import os

app = Flask(__name__)

# ==============================
# TEJGAON, DHAKA
# ==============================

LATITUDE = 23.7630
LONGITUDE = 90.3897

# ==============================
# SOLAR PANEL SETTINGS
# ==============================

PANEL_CAPACITY_KW = 1.0
PANEL_EFFICIENCY = 0.20

TEMP_COEFFICIENT = 0.004

CSV_FILE = "data.csv"


# ==============================
# GET WEATHER DATA
# ==============================

def get_weather_data():

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,

        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "cloud_cover,"
            "wind_speed_10m,"
            "surface_pressure,"
            "uv_index,"
            "shortwave_radiation"
        ),

        "timezone": "Asia/Dhaka"
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    current = data["current"]

    # ==============================
    # WEATHER
    # ==============================

    temperature = current["temperature_2m"]
    humidity = current["relative_humidity_2m"]
    cloud = current["cloud_cover"]
    wind = current["wind_speed_10m"]
    pressure = current["surface_pressure"]
    uv = current["uv_index"]
    radiation = current["shortwave_radiation"]


    # ==============================
    # CLOUD FACTOR
    # ==============================

    cloud_factor = (
        1 - (cloud / 100) * 0.75
    )

    cloud_factor = max(
        0.25,
        cloud_factor
    )


    # ==============================
    # TEMPERATURE FACTOR
    # ==============================

    temperature_factor = (
        1 -
        TEMP_COEFFICIENT *
        max(0, temperature - 25)
    )

    temperature_factor = max(
        0.70,
        temperature_factor
    )


    # ==============================
    # RADIATION FACTOR
    # ==============================

    radiation_factor = radiation / 1000


    # ==============================
    # ESTIMATED SOLAR POWER
    # ==============================

    estimated_power = (

        PANEL_CAPACITY_KW
        * radiation_factor
        * cloud_factor
        * temperature_factor

    )

    estimated_power = min(
        estimated_power,
        PANEL_CAPACITY_KW
    )


    # ==============================
    # DAILY ENERGY
    # ==============================

    daily_energy = (
        estimated_power * 5
    )


    # ==============================
    # CO2 REDUCTION
    # ==============================

    CO2_FACTOR = 0.55

    daily_co2_reduction = (
        daily_energy * CO2_FACTOR
    )


    return {

        "time": current["time"],

        "temperature": temperature,

        "humidity": humidity,

        "cloud": cloud,

        "wind": wind,

        "pressure": pressure,

        "uv": uv,

        "radiation": radiation,

        "panel_capacity":
            PANEL_CAPACITY_KW,

        "panel_efficiency":
            PANEL_EFFICIENCY * 100,

        "cloud_factor":
            round(cloud_factor, 3),

        "temperature_factor":
            round(
                temperature_factor,
                3
            ),

        "estimated_power":
            round(
                estimated_power,
                3
            ),

        "daily_energy":
            round(
                daily_energy,
                2
            ),

        "daily_co2":
            round(
                daily_co2_reduction,
                2
            )
    }


# ==============================
# SAVE CSV
# ==============================

def save_to_csv(data):

    file_exists = os.path.exists(
        CSV_FILE
    )

    with open(
        CSV_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        if not file_exists:

            writer.writerow([
                "time",
                "temperature",
                "humidity",
                "cloud",
                "wind",
                "pressure",
                "uv",
                "radiation",
                "panel_capacity",
                "panel_efficiency",
                "cloud_factor",
                "temperature_factor",
                "estimated_power",
                "daily_energy",
                "daily_co2"
            ])

        writer.writerow([

            data["time"],
            data["temperature"],
            data["humidity"],
            data["cloud"],
            data["wind"],
            data["pressure"],
            data["uv"],
            data["radiation"],
            data["panel_capacity"],
            data["panel_efficiency"],
            data["cloud_factor"],
            data["temperature_factor"],
            data["estimated_power"],
            data["daily_energy"],
            data["daily_co2"]

        ])


# ==============================
# HTML
# ==============================

@app.route("/")
def home():

    return send_from_directory(
        ".",
        "index.html"
    )


# ==============================
# CSS
# ==============================

@app.route("/style.css")
def css():

    return send_from_directory(
        ".",
        "style.css"
    )


# ==============================
# JAVASCRIPT
# ==============================

@app.route("/script.js")
def javascript():

    return send_from_directory(
        ".",
        "script.js"
    )


# ==============================
# WEATHER API
# ==============================

@app.route("/api/weather")
def weather():

    try:

        data = get_weather_data()

        save_to_csv(data)

        return jsonify(data)

    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "error": str(e)
        }), 500


# ==============================
# RUN SERVER
# ==============================

if __name__ == "__main__":

    app.run(
        debug=True
    )