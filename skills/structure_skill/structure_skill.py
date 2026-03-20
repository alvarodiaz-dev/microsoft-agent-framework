from agent_framework import Skill
from textwrap import dedent

def structure_skill():
    return Skill(
        name="structure-generator",
        description="Generate project structure",
        content=dedent("""
You receive a JSON with microservice requirements.
You must return ONLY a valid JSON object. Nothing else.

NO markdown
NO backticks
NO ```json
NO explanations
NO text before or after the JSON
START your response with {
END your response with }

RETURN THIS EXACT OUTPUT STRUCTURE:

{
  "base_dir": "microservices/SERVICE_NAME",
  "package": "com.example.SERVICE_NAME",
  "files": [
    {"path": "pom.xml", "type": "pom"},
    {"path": "src/main/java/com/example/SERVICE_NAME/Application.java", "type": "main"},
    {"path": "src/main/java/com/example/SERVICE_NAME/controller/MainController.java", "type": "controller"},
    {"path": "src/main/java/com/example/SERVICE_NAME/service/MainService.java", "type": "service"},
    {"path": "src/main/java/com/example/SERVICE_NAME/model/MainModel.java", "type": "model"}
  ]
}

Replace SERVICE_NAME with the actual service name from the input (lowercase, no spaces) and always use underscores (_) instead of hyphens (-).
YOUR ENTIRE RESPONSE MUST BE ONLY THE JSON OBJECT. FIRST CHARACTER MUST BE {
""")
    )