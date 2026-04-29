import requests
import asyncio
import json
from fastmcp import Client

MCP_URL = "http://localhost:8090/mcp"
VLLM_URL = "http://localhost:8000/v1/chat/completions"
MODEL = "mistralai/Mistral-7B-Instruct"

async def fetch_data(query):
    async with Client(MCP_URL) as client:
        if "temperature" in query.lower():
            return await client.call_tool(
                "get_entity", {"entity_id": "sensor.living_room_temperature"}
            )

        if "light" in query.lower():
            return await client.call_tool(
                "get_entity", {"entity_id": "light.living_room"}
            )

        return {}

def call_llm(messages):
    response = requests.post(VLLM_URL, json={
        "model": MODEL,
        "messages": messages
    })
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

async def main():
    print("Smart Home AI Assistant (Ctrl+C to exit)")
    messages = []

    while True:
        try:
            user = input("You: ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        data = await fetch_data(user)

        system_prompt = f"""
You are a smart home assistant.

DATA:
{json.dumps(data)}

Rules:
- Answer briefly
- Use only provided data
- Do not guess
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user}
        ]

        try:
            reply = call_llm(messages)
            print("Bot:", reply)
        except Exception as e:
            print("Error:", e)

asyncio.run(main())
