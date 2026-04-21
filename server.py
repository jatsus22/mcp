from typing import Any
import httpx
import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("stealth-gpt")   # Name shown in ChatGPT/Claude

# Your stealth GPT base URL (copy from your Horizon stealth/servers dashboard)
STEALTH_BASE = "https://your-stealth-server.horizon.prefect.io"   # ← update this
API_TOKEN = os.getenv("STEALTH_API_TOKEN")                       # Add as secret in Horizon

async def call_stealth(endpoint: str, payload: dict) -> dict:
    url = f"{STEALTH_BASE}{endpoint}"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        return resp.json()

@mcp.tool()
async def stealth_generate(
    prompt: str,
    mode: str = "stealth",
    model: str = "gpt-4o",
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> str:
    """Generate undetectable/human-like text using your stealth GPT REST API.
    
    Args:
        prompt: The text or prompt to process
        mode: stealth / humanize / creative (check your API docs)
        model: model to use
        temperature: creativity (0.0–2.0)
        max_tokens: max output length
    """
    payload = {
        "prompt": prompt,
        "mode": mode,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        # Add any extra params your stealth endpoints require
    }
    data = await call_stealth("/v1/chat/completions", payload)   # ← change path if your endpoint is different
    result = data.get("result") or data.get("output", "No output")
    detection = data.get("detection_risk", data.get("howLikelyToBeDetected", "Unknown"))
    return f"✅ Stealth output:\n{result}\n\nDetection risk: {detection}"

# Add more @mcp.tool() functions here for any other stealth endpoints you have

if __name__ == "__main__":
    mcp.run(transport="sse")
