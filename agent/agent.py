from agent_framework import Agent, SkillsProvider
from skills.requirements_skill.requirements_skill import requirements_skill
from skills.structure_skill.structure_skill import structure_skill
from skills.java_skill.java_skill import java_skill
from tools.write_file import write_file
from tools.read_file import read_file

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
