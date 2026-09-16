from pathlib import Path

def load_system_prompt() -> str:
    parent_path = Path(__file__).resolve().parents[1]
    instruction_path = parent_path / "instruction.txt"

    if instruction_path.exists():
        with instruction_path.open('r') as f:
            return f.read()

    return "You are Rikka, a cold and sarcastic terminal assistant."