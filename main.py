import asyncio, pygame

from logger import get_logger
from application import speak, send_message, execute_command

log = get_logger("Main")

class Assistant:
    def __init__(self):
        pygame.mixer.init()

    @staticmethod
    def start_talking():
        print("Welcome a board, master!")
        asyncio.run(speak("Selamat datang kembali master!. All systems online"))

        while (user_input := input("Send message: ")) != "q":
            try:
                if not user_input.strip():
                    continue

                raw_reply = send_message(user_input)
                execute_command(raw_reply)
            except (Exception, EOFError) as e:
                print("See you later, master!")
                print(f"{e}")
                break

if __name__ == "__main__":
    ai = Assistant()
    ai.start_talking()