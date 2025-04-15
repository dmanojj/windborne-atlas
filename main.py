from fastapi import FastAPI, Query
import requests
from fastapi.responses import JSONResponse
import json
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import httpx
import asyncio

app = FastAPI()

from dotenv import load_dotenv
import os


load_dotenv()

OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
OPENCAGE_API_KEY = os.getenv('OPENCAGE_API_KEY')

# Serve static files
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
def root():
    return FileResponse("index.html")




@app.get("/hour")
async def get_hour_data(value: str = Query(..., min_length=2, max_length=2)):
    hour = int(value)

    async def fetch_hour_data(h: int):
        if h < 0 or h > 23:
            return None

        hour_str = str(h).zfill(2)
        url = f"https://a.windbornesystems.com/treasure/{hour_str}.json"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)

        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    return data[:10]
            except:
                return None
        return None  # Explicitly return None on 404 or error

    raw_data = await fetch_hour_data(hour)
    if not raw_data:
        return {
            "hour": hour,
            "available": False,
            "message": "Data unavailable for the requested hour."
        }

    points = [
        {"latitude": lat, "longitude": lng, "altitude": alt}
        for lat, lng, alt in raw_data
    ]

    async def fetch_weather(lat, lon):
        url = (
            f"https://api.openweathermap.org/data/2.5/weather?"
            f"lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        )
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            return r.json() if r.status_code == 200 else {}

    async def reverse_geocode(lat: float, lon: float):
        url = f"https://api.opencagedata.com/geocode/v1/json?q={lat}+{lon}&key={OPENCAGE_API_KEY}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if data["results"]:
                    components = data["results"][0]["components"]
                    city = components.get("city") or components.get("town") or components.get("village") or "Unknown City"
                    country = components.get("country", "Unknown Country")
                    return f"{city}, {country}"
        return "Unknown Location"

    def assess_delay(weather: dict) -> bool:
        try:
            visibility = weather.get("visibility", 10000)
            wind_speed = weather.get("wind", {}).get("speed", 0)
            snow = weather.get("snow", {}).get("1h", 0)
            rain = weather.get("rain", {}).get("1h", 0)
            weather_main = weather.get("weather", [{}])[0].get("main", "")
            return (
                visibility < 1000 or
                wind_speed > 10 or
                snow > 0.5 or
                rain > 0.5 or
                weather_main in ["Thunderstorm", "Snow", "Rain", "Extreme"]
            )
        except:
            return False

    weather_data = await asyncio.gather(*[
        fetch_weather(p["latitude"], p["longitude"]) for p in points
    ])

    locations = await asyncio.gather(*[
        reverse_geocode(p["latitude"], p["longitude"]) for p in points
    ])

    enriched_points = []
    for p, w, loc in zip(points, weather_data, locations):
        enriched_points.append({
            **p,
            "weather": w,
            "shipping_delay": assess_delay(w),
            "location": loc
        })

    return {
        "hour": hour,
        "available": True,
        "points": enriched_points
    }