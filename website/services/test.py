from datetime import timedelta, datetime
import requests
import json

today = datetime.now().replace(hour=19, minute=0, second=0, microsecond=0)

headers = {
    "Authorization": "Bearer os_v2_app_e523zuiktraodgpi4ms6nmqhnema4tzkqoquueez7oj3ujkdv2uq56ufcyg36i7kzfxvhspyfrktn2ump5rux6pb2nxrc7wrjtcukxq",  # Tu App API Key aquí
    "Content-Type": "application/json"
}
notification_time = today
payload = {
    "app_id": "2775bcd1-0a9c-40e1-99e8-e325e6b20769",
    "contents":{"en":"Recordatorio: 2ª Ronda ARRECIFE ENVITE TOUR 2025 mañana en Centro de Mayores de Altavista a las 20:00"},
    "include_player_ids": ["2df957d7-d896-40a1-b82f-6ffb8c6e0960"],
    'send_after': notification_time.isoformat()   

}

response = requests.post("https://api.onesignal.com/api/v1/notifications", headers=headers, data=json.dumps(payload))

print(response.status_code)
print(response.text)
