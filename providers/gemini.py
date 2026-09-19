from google import genai
from google.genai import types

from providers.system_prompt import load_system_prompt

def use_gemini(message: list[dict[str,str]], api_key: str, model: str) -> str:
    clients = genai.Client(api_key=api_key)

    config = types.GenerateContentConfig(
        system_instruction=load_system_prompt()
    )
    contents = []
    for msg in message:
        if msg['role'] == 'system':
            continue

        contents.append(
            types.Content(
                role='model' if msg['role'] == 'assistant' else msg['role'],
                parts=[types.Part(msg['content'])]
            )
        )

    response = clients.models.generate_content(
        model=model,
        contents=contents,
        config=config
    )

    return response.text
