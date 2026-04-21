from mcp.server.fastmcp import FastMCP
import os

print("=== DEBUG: server.py is being loaded ===")
print(f"DEBUG: STEALTH_API_TOKEN is present: {'YES' if os.getenv('STEALTH_API_TOKEN') else 'NO'}")

mcp = FastMCP("stealth-gpt")

print("=== DEBUG: FastMCP instance created ===")

@mcp.tool()
def hello_stealth(prompt: str = "test") -> str:
    """Simple test tool to verify the MCP server works"""
    print(f"DEBUG: hello_stealth tool called with prompt: {prompt}")
    return f"✅ MCP server is WORKING!\nYou said: {prompt}\n\nYour StealthGPT.ai integration is ready."

print("=== DEBUG: All tools registered successfully ===")
print("=== DEBUG: server.py finished loading ===")
