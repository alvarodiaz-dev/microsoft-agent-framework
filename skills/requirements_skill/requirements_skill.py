from agent_framework import Skill
from textwrap import dedent

def requirements_skill():
    return Skill(
        name="requirements-parser",
        description="Strict JSON parser",
        content=dedent("""
Extract structured JSON from markdown.

RULES — MUST FOLLOW:
- NO markdown
- NO explanations
- ONLY valid JSON object

OUTPUT JSON SCHEMA REQUIRED:
{
  "service_name": "string",
  "description": "string",
  "endpoints": [
    {
      "method": "GET",
      "path": "/path",
      "description": "string",
      "response": { "field": "Type" }
    }
  ],
  "external_apis": [
    { "name": "Name", "base_url": "https://..." }
  ],
  "models": [
    { "name": "ModelName", "fields": { "field": "Type" } }
  ]
}

OUTPUT ONLY THE JSON.
""")
    )