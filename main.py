from time import sleep
from google import genai
from google.genai import types
import pygame
import edge_tts
from pathlib import Path

import os
import asyncio

from executor import CommandExecutor

class Assistant:
    def __init__(self, model: str = "gemini-2.5-flash"):
        if not os.environ.get("GEMINI_API_KEY"):
            print("Api key not set yet")
            exit(0)
        self.executor = CommandExecutor()

        pygame.mixer.init()
        self.voice_character = "en-US-AvaNeural"

        self.client = genai.Client()
        self.model = model

        instruction_path = Path("instruction.txt")
        if not instruction_path.exists():
            print("Instruction file does not exist")
            exit(0)

        with open(instruction_path, 'r') as file:
            instruction = file.read().strip()

        self.chat = self.client.chats.create(
            model=self.model,
            config=types.GenerateContentConfig(
                system_instruction=instruction,
                temperature=0.7
            )
        )

    def send_message(self, message: str) -> str:
        try:
            response = self.chat.send_message(message)
            return response.text
        except Exception as e:
            return f"An error occured while connecting: {e}"

    def start_talking(self):
        print("Welcome back, master!")

        while (user_input := input("Send message: ")) != "exit":
            try:
                if not user_input.strip():
                    continue

                reply = self.send_message(user_input)
                print(f"Nino: {reply}")
                asyncio.run(self.speak(reply))
            except (Exception, EOFError) as e:
                print("See you later, master!")
                print(f"{e}")
                break

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

    def execute_command(self, text: str):
        print("=== TEST EXTRAK ===")
        c_text, cmds = self.executor.extract_commands(text)
        print(f"Clean Text: {c_text}")
        print(f"Extracted Commands: {cmds}\n")

        print("=== TEST EKSEKUSI ===")
        for c in cmds:
            print(f"Executing '{c}'...")
            output = self.executor.execute_commands(c)
            print(f"Result:\n{output}\n")

if __name__ == "__main__":
    bot = Assistant()
    bot.start_talking()