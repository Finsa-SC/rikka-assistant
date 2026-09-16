from pathlib import Path
from time import sleep
import edge_tts, pygame, asyncio, os
from dotenv import load_dotenv

from .executor import CommandExecutor
from logger import get_logger
from ai_models import use_openrouter

log = get_logger(__name__)

load_dotenv()
API_KEY: str = os.getenv("API_KEY")
MODEL: str = os.getenv("MODEL")
VOICE_ACTOR: str = os.getenv("VOICE_ACTOR")

def send_message(message: str) -> str|None:
    try:
        response = use_openrouter(
            message,
            model=MODEL,
            api_key=API_KEY
        )

        return response
    except Exception as e:
        return f"An error occured while connecting: {e}"

async def speak(text: str):
    tts_file = "rikka_voice.mp3"
    try:
        communicate = edge_tts.Communicate(text=text, voice=VOICE_ACTOR)
        await communicate.save(tts_file)

        pygame.mixer.music.load(tts_file)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            sleep(0.1)

        if Path(tts_file).exists():
            Path(tts_file).unlink()

    except Exception as e:
        print(f"An error occured while trying to play sound: {e}")

executor = CommandExecutor()
def execute_command(raw_text, depth: int = 0):
    if depth > 5:
        return

    clean_text, cmds = executor.extract_commands(raw_text)

    if clean_text:
        print(f"Rikka: {clean_text}")
        asyncio.run(speak(clean_text))

    if cmds:
        exec_results = []
        for cmd in cmds:
            log.info(f"Command request: {cmd}")
            output = executor.execute_commands(cmd)

            exec_results.append(f"Result of '{cmd}':\n{output}")

        system_feedback = f"[SYSTEM_FEEDBACK]\n" + "\n".join(exec_results)
        log.info("Send feedback to ai")
        analysis_reply = send_message(system_feedback)

        execute_command(analysis_reply, depth + 1)