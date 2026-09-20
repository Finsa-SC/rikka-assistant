from openai import OpenAI

def use_cloudflare(message: list[dict[str,str]], model: str, api_key: str, account_id: str) -> str:
    client = OpenAI(
        api_key=api_key,
        base_url=(
            f"https://api.cloudflare.com/client/v4/"
            f"accounts/{account_id}/ai/v1"
        )
    )

    response = client.chat.completions.create(
        model=model,
        messages=message
    )

    return response.choices[0].message.content