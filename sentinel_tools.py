# sentinel_tools.py

import os
from dotenv import load_dotenv
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from typing import List, Dict, Any
from agents import function_tool
import requests
from tokens import open_weather_key
from pydantic import BaseModel
from config import sync_client
from memory import AgentMemory

chat_memory = AgentMemory()
# ────── AUTH SETUP ──────
load_dotenv()

SH_BASE_URL = os.getenv("SH_BASE_URL")    # e.g. https://sh.dataspace.copernicus.eu
TOKEN_URL   = os.getenv("SH_TOKEN_URL")   # CDSE token endpoint
INSTANCE_ID = os.getenv("INSTANCE_ID")    # your instance UUID

_client_id     = os.getenv("SH_CLIENT_ID")
_client_secret = os.getenv("SH_CLIENT_SECRET")

_client = BackendApplicationClient(client_id=_client_id)
_oauth  = OAuth2Session(client=_client)

# fetch and cache token
_oauth.fetch_token(
    token_url=TOKEN_URL,
    client_id=_client_id,
    client_secret=_client_secret,
    include_client_id=True
)

# ────── TOOL FUNCTIONS ──────

@function_tool
def find_scenes(collection: str,
                bbox: List[float],
                time_from: str,
                time_to: str,
                limit: int = 20) -> Dict[str, Any]:
    """
    Search the Sentinel Hub Catalog for STAC features.
    """
    url = f"{SH_BASE_URL}/api/v1/catalog/1.0.0/search"
    body = {
        "collections": [collection],
        "bbox": bbox,
        "datetime": f"{time_from}/{time_to}",
        "limit": limit
    }
    resp = _oauth.post(url, json=body)
    resp.raise_for_status()
    return resp.json()

@function_tool
def process_raster(evalscript: str,
                   bbox: List[float],
                   time_from: str,
                   time_to: str,
                   width: int,
                   height: int,
                   collection: str = "sentinel-2-l2a",
                   mime_type: str = "image/tiff") -> bytes:
    """
    Invoke the Process API to generate a raster (GeoTIFF or PNG).
    """
    url = f"{SH_BASE_URL}/api/v1/process"
    payload = {
        "input": {
            "bounds": {"bbox": bbox},
            "data": [{
                "type": collection,
                "dataFilter": {
                    "timeRange": {"from": time_from, "to": time_to}
                }
            }]
        },
        "evalscript": evalscript,
        "output": {
            "width": width,
            "height": height,
            "responses": [{
                "identifier": "default",
                "format": {"type": mime_type.split("/")[-1]}
            }]
        }
    }
    resp = _oauth.post(url, json=payload)
    resp.raise_for_status()
    return resp.content

@function_tool
def stats(bbox: List[float],
          time_from: str,
          time_to: str,
          reducer: str = "MEAN",
          collection: str = "sentinel-2-l2a") -> Dict[str, Any]:
    """
    Call the Statistical API to compute daily stats over the AOI.
    """
    url = f"{SH_BASE_URL}/api/v1/statistics"
    body = {
        "input": {
            "bounds": {"bbox": bbox},
            "data": [{
                "type": collection,
                "dataFilter": {"timeRange": {"from": time_from, "to": time_to}}
            }]
        },
        "aggregation": {
            "interval": {"type": "DAY"},
            # simple evalscript returning the chosen reducer
            "evalscript": f"return [{reducer}];"
        }
    }
    resp = _oauth.post(url, json=body)
    resp.raise_for_status()
    return resp.json()

class CoutryLatLon(BaseModel):
    country_code: str
    lat: str
    lon: str


@function_tool
def get_country_latitude_longitude(city_name: str):
    """Fetches the country code, latitude and longitude of a given city"""
    sys_prompt = (
        "For the given city name return the country code of the country it is part of. For example if the city is in Romania return RO. If the city is in Germany return DE."
        "Besides the country code return the latitude and the longitude of the city"
    )
    response = sync_client.beta.chat.completions.parse(
        model = "o1",
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": city_name}
        ],
        response_format = CoutryLatLon
    )
    country_code = response.choices[0].message.parsed.country_code
    lat = response.choices[0].message.parsed.lat
    lon = response.choices[0].message.parsed.lon
    return country_code, lat, lon

@function_tool
def get_air_pollution(lat: str, lon: str) -> dict:
    """
    Fetches current air pollution data for the given latitude and longitude
    from OpenWeatherMap.
    """
    url = "http://api.openweathermap.org/data/2.5/air_pollution"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": open_weather_key
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

@function_tool
def get_climatic_conditions(lat: str, lon: str, nr_days: int) -> dict:
    """
    Fetches climatic data for the given latitude and longitude
    from OpenWeatherMap for a given number of days.
    """
    url = "https://pro.openweathermap.org/data/3.0/forecast/climate"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": open_weather_key,
        "cnt": nr_days,
        "units": "metric"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

@function_tool
def get_solar_irradiance(lat: str, lon: str, date: str) -> dict:
    """
    Fetches solar irradiance data for the given latitude and longitude
    from OpenWeatherMap on a given date.
    """
    print("Am intrat in solar irradiance")
    print(date)
    url = "https://api.openweathermap.org/energy/1.0/solar/data"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": open_weather_key,
        "date": date,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

@function_tool
def get_conversation_history():
    """This function retrieves the conversation history"""
    return chat_memory.get_messages()