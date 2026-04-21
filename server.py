from typing import Any
import httpx
import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("stealth-gpt")

STEALTH_BASE = "https://stealthgpt.ai"
API_TOKEN = os.getenv("STEALTH_API_TOKEN")

async def call_stealth(payload: dict) -> dict:
    url = f"{STEALTH_BASE}/api/stealthify"
    headers = {
        "api-token": API_TOKEN,
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, headers=headers, timeout=60.0)
        resp.raise_for_status()
        return resp.json()

@mcp.tool()
async def stealthify(
    prompt: str,
    rephrase: bool = False,
    tone: str = "College",
    mode: str = "Medium",
    qualityMode: str = "quality",
    business: bool = False,
    isMultilingual: bool = True,
    outputFormat: str = "markdown"
) -> str:
    """Stealthify text using StealthGPT.ai (basic endpoint) - makes it undetectable/human-like.
    
    Args:
        prompt: The text or prompt you want to process
        rephrase: Whether to rephrase the content
        tone: College / Professional / Casual / etc.
        mode: Medium / Stealth / etc.
        qualityMode: quality / high / medium / low
        business: Enable business mode
        isMultilingual: Support multiple languages
        outputFormat: markdown / text / html
    """
    payload = {
        "prompt": prompt,
        "rephrase": rephrase,
        "tone": tone,
        "mode": mode,
        "qualityMode": qualityMode,
        "business": business,
        "isMultilingual": isMultilingual,
        "outputFormat": outputFormat
    }
    data = await call_stealth(payload)
    
    result = data.get("result") or data.get("output") or str(data)
    detection = data.get("howLikelyToBeDetected", "Unknown")
    
    return f"✅ Stealthified output:\n{result}\n\nDetection risk: {detection}"
