from agent_framework import tool
import os

@tool(description="Read a file and return its content.")
def read_file(path: str) -> str:
    if not os.path.exists(path):
        return f"File not found: {path}"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
