from agent_framework import Skill
from textwrap import dedent

def github_skill():
    return Skill(
        name="github-publisher",
        description="Publish project to GitHub",
        content=dedent("""
Publish project to GitHub.

STEPS:
1. Create repository
2. Create/update files
3. Commit
4. Push to main

Use available GitHub MCP tools.

INPUT:
{
  "repo_name": "string",
  "files": [
    {"path": "...", "content": "..."}
  ]
}

OUTPUT:
Use tool calls only.
""")
    )