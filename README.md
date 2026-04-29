Local Smart Home AI Assistant

This project implements a fully local AI-powered smart home assistant using Home Assistant, a locally hosted LLM (via vLLM), and an MCP tool server.
The system is designed to answer questions about the smart home environment by dynamically retrieving real-time data from Home Assistant and feeding it into a local language model.

Features
Fully local LLM inference (no cloud APIs)
Real-time smart home data retrieval
Modular architecture using Docker
MCP-based tool system for flexible data access
Context-aware chatbot running in terminal

Architecture
User input is processed by a Python chatbot, which:
Queries MCP tools for relevant Home Assistant data
Builds a dynamic system prompt
Sends the request to a local LLM (vLLM)
Returns a natural language response
User → Chatbot → MCP → Home Assistant
                      ↓
                     vLLM → Response
Tech Stack
- Home Assistant
- vLLM (OpenAI-compatible API)
- MCP (FastMCP)
- Python
- Docker


Example questions
"What is the temperature in the living room?"
"Are the lights on?"
"What's the current state of my home?"




