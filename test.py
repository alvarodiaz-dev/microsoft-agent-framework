import os
import asyncio
import json
from textwrap import dedent
from dotenv import load_dotenv
from agent_framework import Agent, Skill, SkillsProvider, MCPStdioTool
from agent_framework.openai import OpenAIResponsesClient
from tools.write_file import write_file
from tools.read_file import read_file

def create_client():
    return OpenAIResponsesClient(
        api_key=os.getenv("LMSTUDIO_API_KEY"),
        base_url="http://localhost:1234/v1",
        model_id="qwen2.5-14b-instruct"
    )

def github_create_repo_skill():
    return Skill(
        name="github-create-repo",
        description="Create GitHub repository using MCP",
        content=dedent("""
Format EXACTLY a MCP tool call. No explanations.

INPUT JSON:
{
  "repo_name": "name",
  "description": "text",
  "private": false
}

OUTPUT EXACTLY:
{
  "tool": "github.createRepository",
  "arguments": {
    "name": "<repo_name>",
    "description": "<description>",
    "private": <private>
  }
}
""")
    )

def github_upload_file_skill():
    return Skill(
        name="github-upload-file",
        description="Upload file to GitHub repo via MCP",
        content=dedent("""
Format EXACTLY a MCP tool call. No explanations.

INPUT JSON:
{
  "repo": "repo-name",
  "path": "path/in/repo",
  "content": "BASE64_STRING",
  "message": "commit message"
}

OUTPUT EXACTLY:
{
  "tool": "github.writeFile",
  "arguments": {
    "repository": "<repo>",
    "path": "<path>",
    "content_base64": "<content>",
    "message": "<message>"
  }
}
""")
    )


def create_agent(client):

    github_mcp = MCPStdioTool(
        name="github",
        command="node",
        args=["./node_modules/@modelcontextprotocol/server-github/dist/index.js"],
        env={"GITHUB_PAT": os.getenv("GITHUB_PAT")},
        load_prompts=False, 
        load_tools=True  

    )

    return Agent(
        client=client,
        name="microservice-github-agent",
        tools=[github_mcp],
        context_providers=[SkillsProvider(
            skills=[
                github_create_repo_skill(),
                github_upload_file_skill()
            ]
        )]
    )

class GitHubMicroserviceExporter:

    def __init__(self, agent: Agent):
        self.agent = agent

    async def run_skill(self, skill: Skill, payload: dict):
        prompt = f"""
SKILL:
{skill.content}

INPUT:
{json.dumps(payload)}

OUTPUT:
FOLLOW SKILL EXACT RULES.
"""
        response = await self.agent.run(prompt)
        return response.text.strip()

    async def create_repo(self, repo_name: str, description: str):
        call_json = await self.run_skill(
            github_create_repo_skill(),
            {
                "repo_name": repo_name,
                "description": description,
                "private": False
            }
        )
        print("📦 Creating GitHub repo...")
        await self.agent.run(call_json)
        print("✔ Repo created!")

    async def upload_directory(self, repo_name: str, directory: str):
        print(f"⬆ Uploading files from {directory}/")

        for root, dirs, files in os.walk(directory):
            for filename in files:
                local_path = os.path.join(root, filename)
                relative_path = os.path.relpath(local_path, directory)

                with open(local_path, "rb") as f:
                    encoded = f.read().encode("base64") if False else __import__("base64").b64encode(f.read()).decode()

                call_json = await self.run_skill(
                    github_upload_file_skill(),
                    {
                        "repo": repo_name,
                        "path": relative_path.replace("\\", "/"),
                        "content": encoded,
                        "message": f"Add {relative_path}"
                    }
                )

                await self.agent.run(call_json)
                print("  ✔", relative_path)

        print("🎉 Upload complete!")

async def main():
    load_dotenv()

    repo_name = "example-mcp-github-test"

    client = create_client()
    agent = create_agent(client)

    exporter = GitHubMicroserviceExporter(agent)

    await exporter.create_repo(repo_name, "Test repo created via MCP GitHub")

    await exporter.upload_directory(repo_name, "test-project")

if __name__ == "__main__":
    asyncio.run(main())