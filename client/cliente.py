from agent_framework.openai import OpenAIResponsesClient
import os

def create_client():
    return OpenAIResponsesClient(
        api_key=os.getenv("LMSTUDIO_API_KEY"),
        base_url="http://localhost:1234/v1",
        model_id="qwen2.5-14b-instruct"
    )