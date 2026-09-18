import asyncio, pygame, threading
from logger import get_logger
from application import speak, send_message, execute_command
from monitoring.event_queue import event_queue

log = get_logger("Main")

class Assistant:
    def __init__(self):
        pygame.mixer.init()
        self.process_lock = threading.Lock()

    def __process(self, message: str):
        with self.process_lock:
            raw_reply = send_message(message)
            execute_command(raw_reply)

    def event_loop(self):
        while True:
            event = event_queue.get()

            try:
                self.__process(event)
            finally:
                event_queue.task_done()

    def start_talking(self):
        print("Welcome a board, master!")
        asyncio.run(speak("Selamat datang kembali master!. All systems online"))

        threading.Thread(
            target=self.event_loop(),
            daemon=True
        ).start()

        while (user_input := input("Send message: ")) != "\\q":
            try:
                if not user_input.strip():
                    continue

                self.__process(user_input)

            except (Exception, EOFError) as e:
                print("See you later, master!")
                print(f"{e}")
                break

if __name__ == "__main__":
    ai = Assistant()
    ai.start_talking()