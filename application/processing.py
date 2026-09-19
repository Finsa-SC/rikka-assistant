import re
from pathlib import Path
import edge_tts, pygame, asyncio

from .executor import CommandExecutor
from logger import get_logger
from providers import use_openrouter, use_ollama, use_gemini, memory
from config import config

logger = get_logger(__name__)

def send_message(message_str: str, role: str = "user") -> str|None:
    if config.memory_enabled:
        memory.manage_memory(dict(role=role, content=message_str))
    message = memory.message

    for attempt in range(3):
        try:
            match config.provider:
                case "openrouter":
                    response = use_openrouter(
                        message,
                        model=config.model,
                        api_key=config.api_key,
                    )
                case "ollama":
                    response = use_ollama(
                        message,
                        model=config.model,
                    )
                case "gemini":
                    response = use_gemini(
                        message,
                        model=config.model,
                        api_key=config.api_key,
                    )
                case _:
                    raise ValueError(f"Invalid provider got: {config.provider}")

            if response is not None:
                return response

            logger.warning(
                f"AI returned empty response, retrying "
                f"({attempt+1}/3"
            )

        except Exception as e:
            return f"An error occured while connecting: {e}"

    logger.error("AI Failed to return a response after 3 attempts")
    return None

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
                voice=config.voice_actor
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
        logger.warning("The AI limit in using consecutive CMDs has run out")
        return

    clean_text, cmds = executor.extract_commands(raw_text)

    if clean_text and clean_text == "<SKIP>":
        logger.info("AI decide to skip response.")
        return

    # Add Rikka memory
    if raw_text:
        memory.manage_memory(dict(role="assistant", content=raw_text))

    if clean_text:
        print(f"\nRikka: {clean_text}")
        asyncio.run(speak(clean_text))

    if cmds:
        exec_results = []
        for cmd in cmds:
            logger.info(f"Command request: {cmd}")
            output = executor.execute_commands(cmd)

            exec_results.append(
                f"Mode: {cmd['mode']}\n"
                f"Result: {output}"
            )

        system_feedback = f"[SYSTEM_FEEDBACK]\n" + "\n".join(exec_results)
        logger.info("Send feedback to ai")
        analysis_reply = send_message(system_feedback, role="system")

        execute_command(analysis_reply, depth + 1)