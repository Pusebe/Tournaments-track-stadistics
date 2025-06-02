from datetime import timedelta
import requests
import json
from ..config import Config

class OneSignalService:
    def __init__(self):
        self.api_url = "https://api.onesignal.com/api/v1/notifications"
        self.headers = {
            "Authorization": f"Bearer {Config.ONESIGNAL_REST_API_KEY}",
            "Content-Type": "application/json"
        }

    def send_convocation_notification(self, convocation, user, player_ids, token):
        if not player_ids:
            return False

        fecha = convocation.date.strftime('%d/%m/%Y')
        hora = convocation.date.strftime('%H:%M')
        link = f"https://dondecuadre.es/convocation?token={token}"

        payload = {
            "app_id": Config.ONESIGNAL_APP_ID,
            "include_player_ids": player_ids,
            "url": link,
            "contents": {
                "en": f"{convocation.subject} en {convocation.place} el {fecha} a las {hora}. Confirma aquí."
            }
        }

        try:
            response = requests.post(self.api_url, headers=self.headers, data=json.dumps(payload))
            if response.status_code == 200:
                return True
            else:
                print(f"Error OneSignal: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Excepción al enviar notificación: {e}")
            return False


    def schedule_reminder_notification(self, convocation, user, player_ids):
        if not player_ids:
            return False

        notification_time = convocation.date - timedelta(days=1, hours=1)
        notification_body = {
            "app_id": Config.ONESIGNAL_APP_ID,
            'contents': {
                'en': f'Recordatorio: {convocation.subject} mañana en {convocation.place} a las {convocation.date.strftime("%H:%M")}'
            },
            'include_player_ids': player_ids,
            'send_after': notification_time.isoformat()
        }

        try:
            response = requests.post(self.api_url, headers=self.headers, data=json.dumps(notification_body))
            if response.status_code == 200:
                return True
            else:
                print(f"Error OneSignal: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Error enviando recordatorio: {e}")
            return False

    def alert_admin(self, convocation, user, player_ids, token):
        if not player_ids:
            return False

        payload = {
            "app_id": Config.ONESIGNAL_APP_ID,
            "include_player_ids": ['f7744d40-d92f-46e7-8b6f-2de9ca645a3b'], #El dispositivo de Igna
            "contents": {
                "en": f"{user.first_name} acaba de confirmar que irá a {convocation.subject}"
            }
        }

        try:
            response = requests.post(self.api_url, headers=self.headers, data=json.dumps(payload))
            if response.status_code == 200:
                return True
            else:
                print(f"Error OneSignal: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Excepción al enviar notificación: {e}")
            return False