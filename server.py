import os
import sys

print("=== DEBUG START ===")
print("DEBUG: Python version:", sys.version)
print("DEBUG: STEALTH_API_TOKEN present:", "YES" if os.getenv("STEALTH_API_TOKEN") else "NO")
print("DEBUG: Current working directory:", os.getcwd())

from mcp.server.fastmcp import FastMCP

print("DEBUG: Successfully imported FastMCP")

mcp = FastMCP("stealth-gpt")

print("DEBUG: FastMCP instance created successfully")

@mcp.tool()
def hello_stealth(prompt: str = "test") -> str:
    """Simple test tool - this should always work"""
    print(f"DEBUG: Tool 'hello_stealth' was called with prompt = {prompt}")
    return f"✅ MCP SERVER IS ALIVE!\nPrompt received: {prompt}\n\nYour StealthGPT.ai call is ready to be added next."

print("DEBUG: Tool registered successfully")
print("=== DEBUG END - server.py loaded completely ===")
