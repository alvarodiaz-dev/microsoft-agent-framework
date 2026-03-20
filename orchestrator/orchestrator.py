from agent_framework import Agent, Skill, MCPStdioTool
import json
import os
from skills.requirements_skill.requirements_skill import requirements_skill
from skills.structure_skill.structure_skill import structure_skill
from skills.java_skill.java_skill import java_skill
from skills.github_skill.github_skill import github_skill
from tools.write_file import write_file

class MicroserviceAgent:

    def __init__(self, agent: Agent):
        self.agent = agent

    async def run_skill(self, skill: Skill, input_text: str):
        prompt = f"""
EXECUTE THE SKILL EXACTLY.

HARD OUTPUT RULES:
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

        print("STEP 4 — GITHUB")

        async with MCPStdioTool(
            name="github",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-github"],
            env={
                "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN")
            },
            load_prompts=False,
            load_tools=True
        ) as github_mcp:

            self.agent.mcp_tools.append(github_mcp)

            tool_call = await self.run_skill(
                github_skill(),
                json.dumps({
                    "repo_name": service_name,
                    "files": generated_files
                })
            )

            await self.agent.run(tool_call)


