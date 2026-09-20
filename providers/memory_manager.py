from config import config

class MemoryManager:
    def __init__(self, max_memory: int = 0):
        self.message = []
        self.max_message = max_memory

    def should_delete_oldest_message(self) -> bool:
        return len(self.message) >= max_message

    def remove_oldest_message(self):
        if self.should_delete_oldest_message():
            self.message.pop(0)

    def manage_memory(self, message: dict[str, str] | None):
        while self.should_delete_oldest_message():
            self.remove_oldest_message()

        if message:
            self.message.append(message)

max_message = config.max_message
if max_message <= 0:
    max_message = 1

memory = MemoryManager(config.max_message)