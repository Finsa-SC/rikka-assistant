from datetime import datetime
from pathlib import Path
import pygame
import asyncio

from logger import get_logger
from application.executor import CommandExecutor
from application import speak

log = get_logger("Main")

class Assistant:
    def __init__(self, model: str, use_local: bool = False):
        self.executor = CommandExecutor()
        self.use_local = use_local
        self.history = []

        pygame.mixer.init()
        # self.voice_character = "en-US-AvaNeural"
        self.voice_character = "id-ID-GadisNeural"
        # self.voice_character = "ja-JP-NanamiNeural"

        instruction_path = Path("instruction.txt")
        if not instruction_path.exists():
            print("Instruction file does not exist")
            exit(0)
        with open(instruction_path, 'r') as file:
            self.instr_file = file.read().strip()

        self.instruction = f"[SYSTEM INFO] Current Time: {datetime.now()}\n\n{self.instr_file}"

    def start_talking(self):
        print("Welcome a board, master!")
        # asyncio.run(self.speak("Welcome a board, Master!. All systems online"))
        asyncio.run(speak("Selamat datang kembali master!. All systems online"))

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