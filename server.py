from mcp.server.fastmcp import FastMCP
import httpx
import os

mcp = FastMCP("stealth-gpt")

@mcp.tool()
async def stealthify(prompt: str) -> str:
    """Stealthify any text using StealthGPT.ai"""
    token = os.getenv("STEALTH_API_TOKEN")
    url = "https://stealthgpt.ai/api/stealthify"
    headers = {
        "api-token": token,
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "rephrase": False,
        "tone": "College",
        "mode": "Medium",
        "qualityMode": "quality",
        "business": False,
        "isMultilingual": True,
        "outputFormat": "markdown"
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()

    result = data.get("result") or data.get("output") or str(data)
    detection = data.get("howLikelyToBeDetected", "Unknown")
    return f"✅ Stealthified:\n{result}\n\nDetection risk: {detection}"
