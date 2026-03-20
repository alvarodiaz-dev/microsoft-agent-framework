import os, asyncio, json, base64
from textwrap import dedent
from dotenv import load_dotenv
from agent_framework import Agent, Skill, SkillsProvider, MCPStdioTool
from agent_framework.openai import OpenAIResponsesClient
from tools.write_file import write_file
from tools.read_file import read_file

load_dotenv()

def create_client():
    return OpenAIResponsesClient(
        api_key=os.getenv("LMSTUDIO_API_KEY"),
        base_url="http://localhost:1234/v1",
        model_id="qwen2.5-14b-instruct"
    )

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

JSON SCHEMA REQUIRED:
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


def java_skill():
    return Skill(
        name="java-generator",
        description="Generate Spring Boot Java/XML files",
        content=dedent("""
You generate ONE complete Java or XML file for a Spring Boot microservice.

NO markdown, NO backticks, NO explanations
Output ONLY raw source code
FIRST LINE must always be "package ..." or "<?xml"

========================================================
INPUT FORMAT EXAMPLE:
========================================================
{
  "requirements": {
    "service_name": "...",
    "endpoints": [{"method": "GET|POST|PUT|DELETE", "path": "/x/{id}", "description": "...", "response": {"field": "Type"}}],
    "external_apis": [{"name": "...", "base_url": "https://..."}],
    "models": [{"name": "ModelName", "fields": {"field": "Type"}}]
  },
  "file": {"path": "...", "type": "pom|main|controller|service|model"},
  "package": "com.example.servicename"
}

========================================================
ARCHITECTURE RULES — ALWAYS APPLY TO ANY SERVICE:
========================================================
1. Constructor injection ONLY — never @Autowired on fields
2. Controller → calls Service methods — NEVER uses WebClient directly
3. Service → calls WebClient — NEVER has @RequestMapping
4. Model → ONLY fields + getters/setters — NO business logic, NO annotations
5. Use EXACT package from input JSON
6. For EACH endpoint in requirements.endpoints → ONE method in controller + ONE method in service
7. WebClient baseUrl = requirements.external_apis[0].base_url
8. Method names derived from endpoint description (e.g. "Get user by id" → getUserById)
9. Path variables in endpoint.path become @PathVariable params
10. Return type of controller method = model class matching endpoint.response fields

========================================================
TEMPLATE — type=model
========================================================
Use this structure for ANY model. Replace with actual fields from requirements.models:

package <PACKAGE>.model;

public class <ModelName> {
    private <Type1> <field1>;
    private <Type2> <field2>;
    // one field per entry in requirements.models[].fields

    public <Type1> get<Field1>() { return <field1>; }
    public void set<Field1>(<Type1> <field1>) { this.<field1> = <field1>; }
    // one getter+setter per field
}

========================================================
TEMPLATE — type=service
REQUIRED MINIMUN IMPORTS (always include ALL of these):
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import <PACKAGE>.model.<ModelName>;
========================================================
Use this structure. Adapt method names and URI from requirements.endpoints:

package <PACKAGE>.service;

import <PACKAGE>.model.<ModelName>;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

@Service
public class MainService {

    private final WebClient webClient;

    public MainService(WebClient.Builder builder) {
        this.webClient = builder.baseUrl("<requirements.external_apis[0].base_url>").build();
    }

    // ONE method per endpoint:
    // public <ReturnType> <methodName>(<PathVarType> <pathVar>) {
    //     return webClient.get()
    //             .uri("<endpoint.path>", <pathVar>)
    //             .retrieve()
    //             .bodyToMono(<ModelName>.class)
    //             .block();
    // }
}

========================================================
TEMPLATE — type=controller
========================================================
package <PACKAGE>.controller;

import <PACKAGE>.model.<ModelName>;
import <PACKAGE>.service.MainService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api")
public class MainController {

    private final MainService mainService;

    public MainController(MainService mainService) {
        this.mainService = mainService;
    }

    // ONE method per endpoint:
    // @GetMapping("<endpoint.path>")
    // public <ModelName> <methodName>(@PathVariable <Type> <var>) {
    //     return mainService.<methodName>(<var>);
    // }
}

========================================================
TEMPLATE — type=main
========================================================
package <PACKAGE>;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}

========================================================
TEMPLATE — type=pom
- artifactId must be: requirements.service_name lowercase, spaces replaced with hyphens
- Example: "Pokemon Service" → "pokemon-service"
- NEVER use spaces in artifactId
========================================================
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.1.5</version>
    </parent>
    <groupId>com.example</groupId>
    <artifactId><SERVICE_NAME_FROM_REQUIREMENTS></artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <properties>
        <java.version>17</java.version>
    </properties>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-webflux</artifactId>
        </dependency>
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>

========================================================
NOW GENERATE THE FILE.
- Read the "type" field from input to know which template to use
- Replace ALL placeholders with real values from the input JSON
- Generate ALL methods for ALL endpoints in requirements.endpoints
- OUTPUT ONLY THE FINAL CODE. NO explanations. NO markdown.
========================================================
""")
    )

def create_agent(client):
    return Agent(
        client=client,
        name="microservice-architect",
        instructions="You are a strict Spring Boot file generator.",
        context_providers=[SkillsProvider(
            skills=[requirements_skill(), structure_skill(), java_skill()]
        )],
        tools=[write_file, read_file]
    )


class MicroserviceAgent:

    def __init__(self, agent: Agent):
        self.agent = agent

    async def run_skill(self, skill: Skill, input_text: str):
        prompt = f"""
EXECUTE THE SKILL EXACTLY.

OUTPUT RULES - MUST FOLLOW:
NO explanations
NO markdown
NO comments
NO natural language
ONLY the raw file content

SKILL INSTRUCTIONS:
{skill.content}

INPUT:
{input_text}

OUTPUT:
ONLY the file content.
"""
        response = await self.agent.run(prompt)
        return response.text.strip()

    def safe_json(self, text):
        return json.loads(text)

    async def push_to_github(self, repo_name: str, generated_files: list):
        """Push generated files to GitHub using MCP directly (no LLM involved)."""

        github_username = os.getenv("GITHUB_USERNAME")

        async with MCPStdioTool(
            name="github",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-github"],
            env={"GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")},
            load_tools=True,
            load_prompts=False
        ) as github:

            print(f"Creating repository '{repo_name}'...")
            try:
                await github.call_tool(
                    "create_repository",
                    name=repo_name,
                    description=f"Microservice: {repo_name}",
                    private=False,
                    autoInit=True
                )
                print("Repo created")
            except Exception as e:
                print(f"Repo may already exist: {e}")

            print("Initializing main branch...")
            try:
                await github.call_tool(
                    "create_or_update_file",
                    owner=github_username,
                    repo=repo_name,
                    path=".gitkeep",
                    message="chore: initialize repository",
                    content=base64.b64encode(b"").decode("utf-8"),
                    branch="main"
                )
                print("Branch initialized")
            except Exception as e:
                print(f"Branch may already exist: {e}")

            print(f"Pushing {len(generated_files)} files...")
            res = await github.call_tool(
                "push_files",
                owner=github_username,
                repo=repo_name,
                branch="main",
                files=generated_files,
                message="feat: initial microservice generated by agent"
            )
            print("PUSH SUCCESS")
            print(res)

    async def generate(self, markdown: str):

        generated_files = []

        print("STEP 1 — PARSE REQUIREMENTS")
        req = await self.run_skill(requirements_skill(), markdown)
        requirements = self.safe_json(req)

        service_name = requirements["service_name"].lower().replace(" ", "-")

        print("STEP 2 — STRUCTURE")
        struct = await self.run_skill(structure_skill(), json.dumps(requirements))
        structure = self.safe_json(struct)

        base_dir = structure["base_dir"].replace("<service>", service_name)
        package = structure["package"].replace("<service>", service_name)
        package_path = package.replace(".", "/")

        print("STEP 3 — GENERATE FILES")
        for f in structure["files"]:
            file_path = (
                f["path"]
                .replace("<service>", service_name)
                .replace("<package_path>", package_path)
            )

            print("→", file_path)

            code = await self.run_skill(
                java_skill(),
                json.dumps({
                    "requirements": requirements,
                    "file": f,
                    "package": package
                })
            )

            full_path = os.path.join(base_dir, file_path)
            write_file(full_path, code)

            generated_files.append({
                "path": file_path,
                "content": code
            })

        print("STEP 4 — PUSH TO GITHUB")

        await self.push_to_github(
            repo_name=service_name,
            generated_files=generated_files
        )

        print(f"\nMICROSERVICE '{service_name}' GENERATED + PUSHED TO GITHUB")


async def main():
    load_dotenv()
    agent = create_agent(create_client())
    app = MicroserviceAgent(agent)

    markdown = """
# Pokemon Service
## Description: Microservice to retrieve Pokémon information

## Endpoints
- method: GET, path: /pokemon/{name}, description: Get Pokemon details
  response: name(String), height(Integer), weight(Integer)

## External APIs
- name: PokeAPI, base_url: https://pokeapi.co/api/v2

## Data Models
- name: Pokemon, fields: name(String), height(Integer), weight(Integer)
"""

    await app.generate(markdown)


if __name__ == "__main__":
    asyncio.run(main())