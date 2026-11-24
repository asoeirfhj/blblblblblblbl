import os
import random
import requests
from datetime import datetime, timezone

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

REACTIONS = ["👍", "🔥", "❤️", "😂", "🤔", "👀", "💯", "⚡"]

TRIGGER_PROBABILITY = 0.25


def should_act() -> bool:
    kyiv_hour = (datetime.now(timezone.utc).hour + 2) % 24  # UTC+2, летом UTC+3 можешь поправить сам
    if 2 <= kyiv_hour < 6:
        return False
    return random.random() < TRIGGER_PROBABILITY


def get_latest_message_id():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"limit": 1, "allowed_updates": ["channel_post"]}
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if not data.get("ok"):
            print("getUpdates failed:", data)
            return None
        updates = data.get("result", [])
        if not updates:
            return None
        for upd in reversed(updates):
            if "channel_post" in upd:
                return upd["channel_post"]["message_id"]
    except Exception as e:
        print("get latest message error:", e)
    return None


def set_reaction(message_id: int, emoji: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMessageReaction"
    payload = {
        "chat_id": CHAT_ID,
        "message_id": message_id,
        "reaction": [{"type": "emoji", "emoji": emoji}],
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        result = resp.json()
        if result.get("ok"):
            print(f"Reacted {emoji} to message {message_id}")
        else:
            print("setReaction failed:", result)
    except Exception as e:
        print("setReaction error:", e)


def main():
    if not should_act():
        print("Skip this round (character says: not in the mood)")
        return

    msg_id = get_latest_message_id()
    if not msg_id:
        print("No message found, skip")
        return

    emoji = random.choice(REACTIONS)
    set_reaction(msg_id, emoji)


if __name__ == "__main__":
    main()
