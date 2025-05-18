# agents_setup.py

from agents import Agent
from sentinel_tools import find_scenes, process_raster, stats, get_country_latitude_longitude, get_air_pollution, get_climatic_conditions, get_conversation_history, get_solar_irradiance
from config import model_to_use

# 1) CatalogAgent: scene search
catalog_agent = Agent(
    name="CatalogAgent",
    instructions=(
        "Use the find_scenes() tool to query the Sentinel Hub Catalog "
        "and return scene metadata (STAC features) matching the parameters."
    ),
    tools=[find_scenes],
    model=model_to_use
)

# 2) RasterAgent: custom imagery
raster_agent = Agent(
    name="RasterAgent",
    instructions=(
        "Use process_raster() to submit an evalscript + AOI + time window "
        "to the Process API and return the raw bytes of the raster."
    ),
    tools=[process_raster],
    model=model_to_use
)

# 3) StatsAgent: aggregated time-series
stats_agent = Agent(
    name="StatsAgent",
    instructions=(
        "Use stats() to compute daily aggregated statistics (e.g., MEAN NDVI) "
        "over a bounding box and time interval."
    ),
    tools=[stats],
    model=model_to_use
)

# 4) Pollution / Weather data Agent
weather_data_agent = Agent(
    name="WeatherDataAgent",
    instructions=(
        "You are a weather specialist. You will always first use the 'get_country_latitude_longitude' tool to get the country code, latitude and the longitude of a city"
        "Then you will use the rest of the functions to gather necessary data according to user's request."
        "The 'get_air_pollution' tool is used when users ask pollution-related queries."
        "The 'get_solar_irradiance' tool is used when users ask solar irradiance related queries. Before using this tool format the date as 'YYYY-MM-DD'"
        "The 'get_climatic_conditions' tool is used when users ask climate-related queries, other than solar irradiance."

    ),
    tools=[get_country_latitude_longitude, get_air_pollution, get_climatic_conditions, get_solar_irradiance],
    model=model_to_use
)

# 5) DriverAgent: triage/combiner
driver_agent = Agent(
    name="DriverAgent",
    instructions=(
        "You are the EO Copilot triage agent. Always use the 'get_conversation_history' tool first in order to get the current state of the chat memory"
        "For each user query, decide if you should:\n"
        "  • call CatalogAgent (scene search)\n"
        "  • call RasterAgent (imagery)\n"
        "  • call StatsAgent (statistics)\n"
        "  • call WeatherDataAgent (weather data)\n"
        "After receiving the tool outputs, compose a clear, action-oriented summary."
    ),
    handoffs=[catalog_agent, raster_agent, stats_agent, weather_data_agent],
    tools=[get_conversation_history],
    model=model_to_use
)
