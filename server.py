from typing import Any
import httpx
import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("stealth-gpt")

STEALTH_BASE = "https://stealthgpt.ai"
API_TOKEN = os.getenv("STEALTH_API_TOKEN")

async def call_stealth(endpoint: str, payload: dict) -> dict:
    url = f"{STEALTH_BASE}{endpoint}"
    headers = {
        "api-token": API_TOKEN,
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, headers=headers, timeout=300.0)
        resp.raise_for_status()
        return resp.json()

@mcp.tool()
async def stealthify(
    prompt: str,
    rephrase: bool = True,
    tone: str = "neutral",
    mode: str = "stealth",
    qualityMode: str = "high",
    business: bool = True,
    isMultilingual: bool = True,
    detector: str = "all",
    outputFormat: str = "text"
) -> str:
    """Simple stealthify - makes any text undetectable."""
    payload = {
        "prompt": prompt,
        "rephrase": rephrase,
        "tone": tone,
        "mode": mode,
        "qualityMode": qualityMode,
        "business": business,
        "isMultilingual": isMultilingual,
        "detector": detector,
        "outputFormat": outputFormat
    }
    data = await call_stealth("/api/stealthify", payload)
    result = data.get("result") or data.get("output") or str(data)
    detection = data.get("howLikelyToBeDetected", "Unknown")
    return f"✅ Stealth output:\n{result}\n\nDetection risk: {detection}"

@mcp.tool()
async def stealthify_agent(
    prompt: str,
    preset: str = "academic",
    enableFactCheck: bool = True,
    enableImageGeneration: bool = False
) -> str:
    """Advanced Agent mode - better quality + fact-checking."""
    payload = {
        "preset": preset,
        "prompt": prompt,
        "enableFactCheck": enableFactCheck,
        "enableImageGeneration": enableImageGeneration
    }
    data = await call_stealth("/api/stealthify/agent", payload)
    result = data.get("result") or data.get("output") or str(data)
    detection = data.get("howLikelyToBeDetected", "Unknown")
    return f"✅ Agent Stealth Output:\n{result}\n\nDetection risk: {detection}"
