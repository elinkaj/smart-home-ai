import os
import requests
from fastmcp import FastMCP

mcp = FastMCP("smart-home")

HA_URL = os.getenv("HA_URL")
HA_TOKEN = os.getenv("HA_TOKEN")
API_KEY = os.getenv("MCP_API_KEY")


ALLOWED_ENTITIES = {
    "sensor.living_room_temperature",
    "sensor.outdoor_temperature",
    "sensor.humidity",
    "light.living_room",
    "weather.home",
}

MAX_ENTITIES_PER_REQUEST = 10


def check_api_key(api_key: str):
    if not API_KEY:
        raise RuntimeError("MCP_API_KEY env variable not set on server")
    if api_key != API_KEY:
        raise PermissionError("Invalid API key")


def check_entity_allowed(entity_id: str):
    if entity_id not in ALLOWED_ENTITIES:
        raise ValueError(f"Entity not allowed: {entity_id}")


def ha_get(entity_id: str) -> dict:
    url = f"{HA_URL}/api/states/{entity_id}"
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json",
    }
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()


@mcp.tool()
def get_entity(entity_id: str, api_key: str) -> dict:
    """Get a single Home Assistant entity (requires API key)."""
    check_api_key(api_key)
    check_entity_allowed(entity_id)
    return ha_get(entity_id)


@mcp.tool()
def get_multiple(entities: list, api_key: str) -> dict:
    """Get multiple Home Assistant entities (requires API key)."""
    check_api_key(api_key)
    if len(entities) > MAX_ENTITIES_PER_REQUEST:
        raise ValueError(f"Too many entities (max {MAX_ENTITIES_PER_REQUEST})")
    for entity_id in entities:
        check_entity_allowed(entity_id)
    return {e: ha_get(e) for e in entities}


if __name__ == "__main__":
    mcp.run(host="0.0.0.0", port=8090, path="/mcp")
