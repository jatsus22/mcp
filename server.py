from mcp.server.fastmcp import FastMCP
import httpx
import os

mcp = FastMCP("stealth-gpt")

STEALTH_BASE = "https://stealthgpt.ai"
API_TOKEN = os.getenv("STEALTH_API_TOKEN")

if not API_TOKEN:
    raise ValueError("STEALTH_API_TOKEN is not set. Please add it in Railway Variables.")

@mcp.tool()
async def stealthify(
    prompt: str,
    rephrase: bool = True,
    tone: str = "Standard",
    mode: str = "High",
    qualityMode: str = "quality",
    business: bool = False,
    isMultilingual: bool = True,
    outputFormat: str = "markdown"
) -> str:
    """Stealthify any text using StealthGPT.ai"""
    url = f"{STEALTH_BASE}/api/stealthify"
    headers = {
        "api-token": API_TOKEN,
        "Content-Type": "application/json"
    }
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

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()

    result = data.get("result") or data.get("output") or str(data)
    detection = data.get("howLikelyToBeDetected", "Unknown")
    return f"✅ Stealthified output:\n{result}\n\nDetection risk: {detection}"

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    mcp.run(transport="sse", port=port)
