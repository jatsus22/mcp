import os
import httpx
from mcp.server.fastmcp import FastMCP

# --- CONFIGURATION ---
port = int(os.getenv("PORT", 8080))
# Using 'www' to avoid the 308 redirect we saw earlier
STEALTH_BASE = "https://www.stealthgpt.ai"
API_TOKEN = os.getenv("STEALTH_API_TOKEN")

if not API_TOKEN:
    print("⚠️  BRIDGE FAILURE: STEALTH_API_TOKEN missing.")
else:
    print(f"✅ BRIDGE SUCCESS: Token loaded (Length: {len(API_TOKEN)}).")

mcp = FastMCP("stealth-gpt", host="0.0.0.0", port=port)

@mcp.tool()
async def stealthify(
    prompt: str,
    rephrase: bool = True,
    tone: str = "Standard",
    mode: str = "Medium",
    qualityMode: str = "quality",
    isMultilingual: bool = True
) -> str:
    """
    Transform text to be undetectable by AI detectors.
    
    Args:
        prompt: The text to humanize.
        rephrase: True to rewrite, False to generate.
        tone: 'Standard', 'HighSchool', 'College', or 'PhD'.
        mode: 'Low', 'Medium', or 'High'.
        qualityMode: Set to 'quality'.
        isMultilingual: Set to True for non-English support.
    """
    # --- DATA CLEANING (Fixes the 400 Error) ---
    # 1. Map lowercase tones to the exact casing the API requires
    tone_map = {
        "standard": "Standard",
        "highschool": "HighSchool",
        "college": "College",
        "phd": "PhD"
    }
    mode_map = {
        "low": "Low",
        "medium": "Medium",
        "high": "High"
    }
    
    clean_tone = tone_map.get(tone.lower(), "Standard")
    clean_mode = mode_map.get(mode.lower(), "Medium")

    url = f"{STEALTH_BASE}/api/stealthify"
    headers = {
        "api-token": API_TOKEN,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # We include 'business' as False just to match the API's example exactly
    payload = {
        "prompt": prompt,
        "rephrase": rephrase,
        "tone": clean_tone,
        "mode": clean_mode,
        "qualityMode": qualityMode,
        "isMultilingual": isMultilingual,
        "business": False,
        "outputFormat": "markdown"
    }

    # Debug: Print the payload to Railway logs so we can see what we're sending
    print(f"DEBUG: Sending request with tone='{clean_tone}' and mode='{clean_mode}'")

    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            resp = await client.post(url, json=payload, headers=headers, timeout=60.0)
            
            # If it fails, capture the error message from the API
            if resp.status_code != 200:
                return f"❌ API Error {resp.status_code}: {resp.text}"
                
            data = resp.json()
            result = data.get("result") or "No output received."
            score = data.get("howLikelyToBeDetected", "N/A")
            
            return f"### ✅ Stealthified Result\n\n{result}\n\n**Human Score:** {score}/100"
            
        except Exception as e:
            return f"❌ Connection Error: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="sse")
