import os
import httpx
from mcp.server.fastmcp import FastMCP

# --- 1. CONFIGURATION ---
# Railway provides the 'PORT' environment variable automatically
port = int(os.getenv("PORT", 8080))
STEALTH_BASE = "https://www.stealthgpt.ai"

# --- 2. THE TOKEN BRIDGE ---
# This looks for the name we defined in the Railway Dashboard
API_TOKEN = os.getenv("STEALTH_API_TOKEN")

# This print statement is for your Railway Logs
if not API_TOKEN:
    print("⚠️  BRIDGE FAILURE: The code cannot see 'STEALTH_API_TOKEN'.")
    print("Check Railway Variables to ensure it is linked correctly.")
else:
    print(f"✅ BRIDGE SUCCESS: Token loaded (Length: {len(API_TOKEN)}).")

# --- 3. INITIALIZE SERVER ---
mcp = FastMCP("stealth-gpt", host="0.0.0.0", port=port)

@mcp.tool()
async def stealthify(
    prompt: str,
    rephrase: bool = True,
    tone: str = "Standard",
    mode: str = "Medium",
    qualityMode: str = "quality",
    isMultilingual: bool = True,
    outputFormat: str = "markdown"
) -> str:
    """
    Rewrite text to be undetectable by AI detectors (like Turnitin).
    
    Args:
        prompt: The text content you want to humanize.
        rephrase: Set to True to rewrite existing text.
        tone: 'Standard', 'HighSchool', 'College', or 'PhD'.
        mode: 'High', 'Medium', or 'Low'.
        qualityMode: Use 'quality' for best human-like results.
    """
    if not API_TOKEN or API_TOKEN == "PENDING":
        return "❌ Error: StealthGPT API Token is not configured in Railway."

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
        "isMultilingual": isMultilingual,
        "outputFormat": outputFormat
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, json=payload, headers=headers, timeout=60.0)
            resp.raise_for_status()
            data = resp.json()
            
            result = data.get("result") or data.get("output") or "No output received."
            detection = data.get("howLikelyToBeDetected", "Unknown")
            
            return f"### ✅ Stealthified Output\n\n{result}\n\n**Safety Score:** {detection}/100"
        except Exception as e:
            return f"❌ API Error: {str(e)}"

if __name__ == "__main__":
    # Start the MCP server using SSE
    mcp.run(transport="sse")
