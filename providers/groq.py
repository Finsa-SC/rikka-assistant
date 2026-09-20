from groq import Groq

def use_groq(message: list[dict[str,str]], model: str, api_key: str) -> str:
    client = Groq(
        api_key=api_key,
    )

    response = client.chat.completions.create(
        model=model,
        messages=message,
        tool_choice="none",
        reasoning_effort='low'
    )

    return response.choices[0].message.content