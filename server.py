import os
import httpx
from mcp.server.fastmcp import FastMCP

# --- 1. CONFIGURATION ---
port = int(os.getenv("PORT", 8080))
STEALTH_BASE = "https://www.stealthgpt.ai" # Includes 'www' to avoid redirects
API_TOKEN = os.getenv("STEALTH_API_TOKEN")

if not API_TOKEN:
    print("⚠️  STATUS: API Token missing in Railway.")
else:
    print(f"✅ STATUS: Token loaded. Server active on port {port}.")

# Initialize FastMCP
mcp = FastMCP("stealth-gpt", host="0.0.0.0", port=port)

@mcp.tool()
async def stealthify(
    prompt: str,
    rephrase: bool = True,
    tone: str = "Standard",
    mode: str = "Low",           # Defaulted to Low for maximum savings
    isMultilingual: bool = False
) -> str:
    """
    Rewrite text to be undetectable while strictly staying on the standard (low-cost) tier.
    
    Args:
        prompt: The text to humanize.
        rephrase: True to rewrite text.
        tone: 'Standard', 'HighSchool', 'College', or 'PhD'.
        mode: 'Low' (Cheapest), 'Medium', or 'High'.
    """
    
    # --- 2. THE "COST-LOCK" LOGIC ---
    # We force tone/mode to Title Case to satisfy the API's strict 400-error requirements
    clean_tone = tone.title() if tone.lower() != "phd" else "PhD"
    clean_mode = mode.title()

    url = f"{STEALTH_BASE}/api/stealthify"
    headers = {
        "api-token": API_TOKEN,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # HARDCODED: 'business' is set to False here so it can NEVER be True
    payload = {
        "prompt": prompt,
        "rephrase": rephrase,
        "tone": clean_tone,
        "mode": clean_mode,
        "qualityMode": "quality",
        "isMultilingual": isMultilingual,
        "business": False,         # LOCKED: Strictly False to prevent 10x cost
        "outputFormat": "markdown"
    }

    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            resp = await client.post(url, json=payload, headers=headers, timeout=60.0)
            
            if resp.status_code != 200:
                return f"❌ API Error {resp.status_code}: {resp.text}"
                
            data = resp.json()
            result = data.get("result") or data.get("output") or "No output received."
            score = data.get("howLikelyToBeDetected", "N/A")
            
            return (
                f"### ✅ Stealthified Result (Standard Tier)\n\n{result}\n\n"
                f"---\n"
                f"**Safety Check:**\n"
                f"* **Billing Tier:** Standard (Business: False)\n"
                f"* **Human Score:** {score}/100"
            )
            
        except Exception as e:
            return f"❌ Connection Error: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="sse")
