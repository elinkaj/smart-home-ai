import os
import requests
from fastmcp import FastMCP

mcp = FastMCP("smart-home")

HA_URL = os.getenv("HA_URL")
HA_TOKEN = os.getenv("HA_TOKEN")

def ha_get(entity_id):
    url = f"{HA_URL}/api/states/{entity_id}"
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json",
    }
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()

@mcp.tool()
def get_entity(entity_id: str):
    """Get single Home Assistant entity"""
    return ha_get(entity_id)

@mcp.tool()
def get_multiple(entities: list):
    """Get multiple entities"""
    return {e: ha_get(e) for e in entities}

if __name__ == "__main__":
    mcp.run(host="0.0.0.0", port=8090, path="/mcp")
