from openai import OpenAI
from providers.system_prompt import load_system_prompt

def use_openrouter(message: list[dict[str,str]], api_key, model:str="cohere/north-mini-code:free") -> str:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": load_system_prompt()},
            *message,
        ]
    )
    return response.choices[0].message.content
