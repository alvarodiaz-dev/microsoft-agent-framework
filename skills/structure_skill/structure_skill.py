from agent_framework import Skill
from textwrap import dedent

def structure_skill():
    return Skill(
        name="structure-generator",
        description="Generate project structure",
        content=dedent("""
Input: JSON with requirements.

Return ONLY JSON:

Example output:
{
  "base_dir": "microservices/<service>",
  "package": "com.example.<service>",
  "files": [
    {"path": "pom.xml", "type": "pom"},

    {"path": "src/main/java/<package_path>/application/Application.java", "type": "main"},
    {"path": "src/main/java/<package_path>/controller/MainController.java", "type": "controller"},
    {"path": "src/main/java/<package_path>/service/MainService.java", "type": "service"},
    {"path": "src/main/java/<package_path>/model/MainModel.java", "type": "model"}
  ]
}

package_path = package.replace(".", "/")
""")
    )
