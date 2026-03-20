from agent_framework import tool
import os

@tool(description="Write content to a file, creating parent directories")
def write_file(path: str, content):
    import json
    import os

    os.makedirs(os.path.dirname(path), exist_ok=True)

    if not isinstance(content, str):
        content = json.dumps(content, indent=2)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return f"File written: {path}"