import os
import requests

device_key = os.getenv('BARK_DEVICE_KEY')

def send_bark_notification(title: str, body: str, group_name: str) -> None:
    """
    Send a push notification via Bark (iOS) service.
    :param device_key: Your Bark device key/token
    :param title: Notification title
    :param body: Notification message body
    """
    if not device_key:
        return
    # Construct Bark URL (automatic URL-encoding of title/body is recommended if needed)
    bark_url = f"https://api.day.app/{device_key}/{title}/{body}?group={group_name}"
    try:
        requests.get(bark_url)
    except Exception as e:
        print(f"Failed to send Bark notification: {e}")