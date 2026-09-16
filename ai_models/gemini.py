from google import genai
from google.genai import types

from ai_models.system_prompt import load_system_prompt

def use_gemini(message: str, api_key: str, model: str) -> str:
    clients = genai.Client(api_key=api_key)

    config = types.GenerateContentConfig(
        system_instruction=load_system_prompt()
    )

    response = clients.models.generate_content(
        model=model,
        contents=message,
        config=config
    )

    return response.text
