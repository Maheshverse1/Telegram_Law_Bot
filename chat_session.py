# chat_session.py

class ChatSession:
    def __init__(self):
        self.history = []

    def add_user_message(self, message):
        self.history.append({"role": "user", "content": message})

    def add_bot_message(self, message):
        self.history.append({"role": "bot", "content": message})

    def reset(self):
        self.history = []

    def get_history(self):
        return self.history

    def format_for_prompt(self):
        return "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in self.history])
