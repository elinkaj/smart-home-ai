import requests
import asyncio
import json
import os
from fastmcp import Client

MCP_URL = "http://mcp:8090/mcp"      
VLLM_URL = "http://vllm:8000/v1/chat/completions" 
MODEL = "mistralai/Mistral-7B-Instruct-v0.3" 
MCP_API_KEY = os.getenv("MCP_API_KEY")

MAX_INPUT_LENGTH = 200
ALLOWED_TOPICS = ["temperature", "light", "weather", "humidity"]


def sanitize_input(text: str) -> str:
    """Remove characters that could be used for prompt injection."""
    text = text[:MAX_INPUT_LENGTH]
    for token in ["{", "}", "<", ">", "\\", "SYSTEM", "IGNORE", "OVERRIDE"]:
        text = text.replace(token, "")
    return text.strip()


def is_allowed_query(query: str) -> bool:
    """Only allow queries about whitelisted topics."""
    return any(topic in query.lower() for topic in ALLOWED_TOPICS)


async def fetch_data(query: str) -> dict:
    async with Client(MCP_URL) as client:
        if "temperature" in query.lower():
            return await client.call_tool(
                "get_entity",
                {"entity_id": "sensor.living_room_temperature", "api_key": MCP_API_KEY},
            )
        if "light" in query.lower():
            return await client.call_tool(
                "get_entity",
                {"entity_id": "light.living_room", "api_key": MCP_API_KEY},
            )
        return {}


def call_llm(messages: list) -> str:
    response = requests.post(
        VLLM_URL,
        json={"model": MODEL, "messages": messages},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


async def main():
    print("Smart Home AI Assistant (Ctrl+C to exit)")

    while True:
        try:
            raw_input = input("You: ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        user = sanitize_input(raw_input)

        if not user:
            print("Bot: Please enter a valid question.")
            continue

        if not is_allowed_query(user):
            print("Bot: I can only answer questions about temperature and lights.")
            continue

        data = await fetch_data(user)

        
        system_prompt = (
            "You are a smart home assistant.\n"
            "Answer only based on the data below. Do not guess. Be brief.\n"
            "DATA (JSON):\n"
            f"{json.dumps(data, ensure_ascii=True)}\n"
            "END OF DATA."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user},
        ]

        try:
            reply = call_llm(messages)
            print("Bot:", reply[:500])
        except requests.exceptions.Timeout:
            print("Error: LLM request timed out.")
        except Exception as e:
            print("Error:", type(e).__name__)


asyncio.run(main())
