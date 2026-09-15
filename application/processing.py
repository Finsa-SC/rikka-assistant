from pathlib import Path
from time import sleep
from openai import OpenAI
import edge_tts, pygame, asyncio, os
from dotenv import load_dotenv

load_dotenv()
API_KEY: str = os.getenv("api_key")
MODEL: str = os.getenv("model")

def send_message(self, message: str, save_history: bool = True) -> str|None:
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=API_KEY,
        )

        parent_dir = Path(__file__).resolve().parent
        instruction_path = parent_dir / "instruction.txt"

        with instruction_path.open('r') as file:
            system_prompt = file.read()

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"An error occured while connecting: {e}"


async def speak(self, text: str):
    tts_file = "miko_voice.mp3"
    try:
        communicate = edge_tts.Communicate(text=text, voice=self.voice_character)
        await communicate.save(tts_file)

        pygame.mixer.music.load(tts_file)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            sleep(0.1)

        if Path(tts_file).exists():
            Path(tts_file).unlink()

    except Exception as e:
        print(f"An error occured while trying to play sound: {e}")

def execute_command(raw_text, depth: int = 0):
    if depth > 5:
        return

    clean_text, cmds = executor.extract_commands(raw_text)

    if clean_text:
        print(f"Miko: {clean_text}")
        asyncio.run(speak(clean_text))

    if cmds:
        exec_results = []
        for cmd in cmds:
            log.info(f"Command request: {cmd}")
            output = executor.execute_commands(cmd)

            exec_results.append(f"Result of '{cmd}':\n{output}")

        system_feedback = f"[SYSTEM_FEEDBACK]\n" + "\n".join(exec_results)
        log.info("Send feedback to ai")
        analysis_reply = send_message(system_feedback, save_history=False)

        execute_command(analysis_reply, depth + 1)