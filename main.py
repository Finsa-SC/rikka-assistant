from datetime import datetime
from time import sleep

from pathlib import Path
from google.genai import types

import pygame
import edge_tts
import asyncio, os

from logger import get_logger
from executor import CommandExecutor

log = get_logger("Main")

class Assistant:
    def __init__(self, model: str, use_local: bool = False):
        self.executor = CommandExecutor()
        self.use_local = use_local
        self.history = []

        pygame.mixer.init()
        self.voice_character = "en-US-AvaNeural"
        # self.voice_character = "ja-JP-NanamiNeural"

        instruction_path = Path("instruction.txt")
        if not instruction_path.exists():
            print("Instruction file does not exist")
            exit(0)
        with open(instruction_path, 'r') as file:
            self.instr_file = file.read().strip()

        self.instruction = f"[SYSTEM INFO] Current Time: {datetime.now()}\n\n{self.instr_file}"

        if self.use_local:
            self._init_ollama(model)
        else:
            self._init_gemini(model or "gemini-2.5-flash")


    def _init_gemini(self, model: str):
        from google import genai

        if not os.environ.get("GEMINI_API_KEY"):
            print("Api key not set yet")
            exit(0)

        self.client = genai.Client()
        self.model = model

    def _init_ollama(self, model: str):
        import ollama
        self.ollama = ollama
        self.model = model
        self.history = [{"role": "system", "content": self.instruction}]

    def start_talking(self):
        print("Welcome a board, master!")
        asyncio.run(self.speak("Welcome a board, Master!. All systems online"))

        while (user_input := input("Send message: ")) != "q":
            try:
                if not user_input.strip():
                    continue

                raw_reply = self.send_message(user_input)
                self.execute_command(raw_reply)
            except (Exception, EOFError) as e:
                print("See you later, master!")
                print(f"{e}")
                break

    def send_message(self, message: str, save_message: bool = True) -> str:
        try:
            if self.use_local:
                self.history.append({"role": "user", "content": message})
                response = self.ollama.chat(model=self.model, messages=self.history)
                reply = response["message"]["content"]
                self.history.append({"role": "assistant", "content": reply})
                return reply
            else:
                formated_messages = []
                for msg in self.history:
                    role = "user" if msg["role"] == "user" else "model"
                    formated_messages.append(
                        types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])])
                    )

                clean_text = " ".join(message.split())
                formated_messages.append(
                    types.Content(role="user", parts=[types.Part.from_text(text=clean_text)])
                )

                response = self.client.models.generate_content(
                    model=self.model,
                    contents=formated_messages,
                    config=types.GenerateContentConfig(
                        system_instruction=self.instruction,
                        temperature=0.7
                    )
                )
                reply = response.text

                if save_history:
                    self.history.append({"role": "user", "content": message})
                    self.history.append({"role": "assistant", "content": reply})

                if len(self.history) > 10:
                    self.history = self.history[-10:]

                return reply

        except Exception as e:
            return f"An error occured while connecting: {e}"

    async def speak(self, text: str):
        tts_file = "nino_voice.mp3"
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

    def execute_command(self, raw_text, depth: int = 0):
        if depth > 5:
            return

        clean_text, cmds = self.executor.extract_commands(raw_text)

        if clean_text:
            print(f"Nino: {clean_text}")
            asyncio.run(self.speak(clean_text))

        if cmds:
            exec_results = []
            for cmd in cmds:
                log.info(f"Command request: {cmd}")
                output = self.executor.execute_commands(cmd)

                exec_results.append(f"Result of '{cmd}':\n{output}")

            system_feedback = f"[SYSTEM_FEEDBACK]\n" + "\n".join(exec_results)
            log.info("Send feedback to ai")
            analysis_reply = self.send_message(system_feedback)

            self.execute_command(analysis_reply, depth + 1)

if __name__ == "__main__":
    bot = Assistant("qwen2.5-coder:7b", use_local=True)
    #bot = Assistant("gemini-2.0-flash")
    bot.start_talking()
