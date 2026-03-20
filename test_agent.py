import asyncio
from dotenv import load_dotenv
from client.cliente import create_client
from agent.agent import create_agent
from orchestrator.orchestrator import MicroserviceAgent

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