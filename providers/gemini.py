from google import genai
from google.genai import types

def use_gemini(message: list[dict[str,str]], api_key: str, model: str) -> str:
    clients = genai.Client(api_key=api_key)

    system_message = [
        msg['content']
        for msg in message
        if msg['role'] == 'system'
    ]

    config = types.GenerateContentConfig(
        system_instruction="\n\n".join(system_message)
    )
    contents = []
    for msg in message:
        if msg['role'] == 'system':
            continue

        contents.append(
            types.Content(
                role='model' if msg['role'] == 'assistant' else msg['role'],
                parts=[types.Part(text=msg['content'])]
            )
        )

    response = clients.models.generate_content(
        model=model,
        contents=contents,
        config=config
    )

    return response.text
