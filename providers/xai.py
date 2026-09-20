from openai import OpenAI

def use_xai(message: list[dict[str, str]], api_key: str, model: str) -> str:
    client = OpenAI(
        base_url="https://api.x.ai/v1",
        api_key=api_key
    )

    response = client.chat.completions.create(
        model=model,
        message=message,
    )

    return response.choices[0].message.content