import ollama
from ai_models.system_prompt import load_system_prompt

def use_ollama(message: str, model: str="qwen2.5-coder:7b", role: str = "user") -> str:
    response = ollama.chat(
        model=model,
        messages=[
            {
                'role': 'system',
                'content': load_system_prompt()
            },
            {
                'role': role,
                'content': message
            }
        ]
    )

    reply = response['message']['content']

    return reply