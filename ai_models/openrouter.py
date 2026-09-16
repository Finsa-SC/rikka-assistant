from openai import OpenAI

def use_openrouter(message: str, model: str, api_key) -> str:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ]
    )
    return response.choices[0].message.content
