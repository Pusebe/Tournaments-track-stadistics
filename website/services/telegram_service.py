import requests
from ..config import Config

class TelegramService:
    def __init__(self):
        self.bot_token = Config.TELEGRAM_TOKEN
        self.chat_id = Config.TELEGRAM_GROUP_ID
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def send_message(self, text: str):
        payload = {
            "chat_id": self.chat_id,
            "text": text
        }
        response = requests.post(self.api_url, data=payload)
        return response.ok