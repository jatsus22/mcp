import os
import httpx
from mcp.server.fastmcp import FastMCP

# 1. Config
port = int(os.getenv("PORT", 8080))
STEALTH_BASE = "https://www.stealthgpt.ai" # Includes 'www' for stability
API_TOKEN = os.getenv("STEALTH_API_TOKEN")

if not API_TOKEN:
    print("⚠️  BRIDGE FAILURE: STEALTH_API_TOKEN missing from Railway variables.")
else:
    print(f"✅ BRIDGE SUCCESS: API Token loaded. Server on port {port}.")

mcp = FastMCP("stealth-gpt", host="0.0.0.0", port=port)

@mcp.tool()
async def stealthify(prompt: str) -> str:
    """
    Transform text to be undetectable by AI detectors.
    This tool uses optimized 'Standard' settings to minimize cost.
    """
    url = f"{STEALTH_BASE}/api/stealthify"
    headers = {
        "api-token": API_TOKEN,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # 2. HARDCODED LOCKS (ChatGPT cannot change these)
    payload = {
        "prompt": prompt,
        "rephrase": True,
        "tone": "Standard",         # Cheapest/Most reliable tone
        "mode": "High",              # Lowest word consumption mode
        "qualityMode": "quality",
        "isMultilingual": False,    # Disabled to prevent translation word-count bloat
        "business": False,          # STRICTLY FALSE: Confirms standard $0.20/1k billing
        "outputFormat": "markdown"
    }

    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            resp = await client.post(url, json=payload, headers=headers, timeout=60.0)
            
            # Catch errors like 'out of words' or 'invalid token'
            if resp.status_code != 200:
                return f"❌ API Error {resp.status_code}: {resp.text}"
                
            data = resp.json()
            # The API returns 'result', but we handle 'output' as a backup
            result = data.get("result") or data.get("output") or "No output received."
            score = data.get("howLikelyToBeDetected", "N/A")
            
            return (
                f"### ✅ Stealthified Result\n\n{result}\n\n"
                f"---\n"
                f"**Billing Protection:** Standard Tier Active (Business=False)\n"
                f"**AI Detection Score:** {score}/100"
            )
            
        except Exception as e:
            return f"❌ Connection Error: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="sse")
