import asyncio, pygame
import time
import threading
from logger import get_logger
from application import speak, send_message, execute_command
from monitoring.monitor import polling_monitor, event_watcher

log = get_logger("Main")

class Assistant:
    def __init__(self):
        pygame.mixer.init()
        self.process_lock = threading.Lock()

    def __process(self, message: str):
        with self.process_lock:
            raw_reply = send_message(message)
            execute_command(raw_reply)

    def monitoring_loop(self):
        while True:
            event = polling_monitor()

            if event:
                self.__process(f"[SYSTEM_TROUBLE]\n{event}")

            time.sleep(60)

    def event_watch(self):
        event_watcher(self.handle_system_event)

    def handle_system_event(self, event):
        self.__process(f"[SYSTEM_TROUBLE]\n{event}")

    def start_talking(self):
        print("Welcome a board, master!")
        asyncio.run(speak("Selamat datang kembali master!. All systems online"))

        threading.Thread(
            target=self.monitoring_loop,
            daemon=True
        ).start()

        threading.Thread(
            target=self.event_watch,
            daemon=True
        ).start()

        while (user_input := input("Send message: ")) != "q":
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