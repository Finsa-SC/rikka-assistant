import re
from pathlib import Path
import edge_tts, pygame, asyncio, os
from dotenv import load_dotenv

from ai_models.gemini import use_gemini
from .executor import CommandExecutor
from logger import get_logger
from ai_models import use_openrouter, use_ollama

log = get_logger(__name__)

load_dotenv()
PROVIDER: str = os.getenv("PROVIDER")
API_KEY: str|None = os.getenv("API_KEY")
MODEL: str = os.getenv("MODEL")
VOICE_ACTOR: str = os.getenv("VOICE_ACTOR")

def send_message(message: str, role: str = "user") -> str|None:
    try:
        match PROVIDER:
            case "openrouter":
                response = use_openrouter(
                    message,
                    model=MODEL,
                    api_key=API_KEY
                )
            case "ollama":
                response = use_ollama(
                    message,
                    model=MODEL,
                    role=role
                )
            case "gemini":
                response = use_gemini(
                    message,
                    model=MODEL,
                    api_key=API_KEY,
                )
            case _:
                raise ValueError(f"Invalid provider got: {PROVIDER}")

        return response
    except Exception as e:
        return f"An error occured while connecting: {e}"

async def speak(text: str):
    chunks = re.split(r'(?<=[.!?])\s+', text.strip())
    queue = asyncio.Queue()

    async def generate():
        for i, chunk in enumerate(chunks):
            if chunk is None:
                continue

            filename = f"audio/rikka_voice_{i}.mp3"

            communicate = edge_tts.Communicate(
                text=chunk,
                voice=VOICE_ACTOR
            )

            await communicate.save(filename)
            await queue.put(filename)
        await queue.put(None)
    async def play():
        while True:
            filename = await queue.get()

            if filename is None:
                break

            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)

            Path(filename).unlink(missing_ok=True)
    await asyncio.gather(
        generate(),
        play()
    )

executor = CommandExecutor()
def execute_command(raw_text, depth: int = 0):
    if depth > 5:
        return

    clean_text, cmds = executor.extract_commands(raw_text)

    if clean_text and clean_text == "<SKIP>":
        log.info("AI decide to skip response.")
        return

    if clean_text:
        print(f"\nRikka: {clean_text}")
        asyncio.run(speak(clean_text))

    if cmds:
        exec_results = []
        for cmd in cmds:
            log.info(f"Command request: {cmd}")
            output = executor.execute_commands(cmd)

            exec_results.append(
                f"Mode: {cmd['mode']}\n"
                f"Result: {output}"
            )

        system_feedback = f"[SYSTEM_FEEDBACK]\n" + "\n".join(exec_results)
        log.info("Send feedback to ai")
        analysis_reply = send_message(system_feedback)

        execute_command(analysis_reply, depth + 1)