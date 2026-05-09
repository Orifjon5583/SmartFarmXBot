import json
import urllib.error
import urllib.request

from backend.config import Config
from backend.services.storage import read_settings, write_settings


def _telegram_settings():
    settings = read_settings()
    return settings.get("telegram", {})


def save_telegram_settings(token, chat_id, enabled=True):
    settings = read_settings()
    settings["telegram"] = {
        "token": (token or "").strip(),
        "chatId": (chat_id or "").strip(),
        "enabled": bool(enabled),
    }
    write_settings(settings)
    return public_telegram_settings(settings["telegram"])


def public_telegram_settings(settings=None):
    settings = settings or _telegram_settings()
    token = settings.get("token", "")
    return {
        "chatId": settings.get("chatId", ""),
        "enabled": settings.get("enabled", False),
        "configured": bool(token and settings.get("chatId")),
        "tokenMasked": f"{token[:8]}..." if token else "",
    }


def verify_telegram(token, chat_id):
    token = (token or "").strip()
    chat_id = (chat_id or "").strip()

    if not token or not chat_id:
        return False, "Bot tokeni va Chat ID majburiy."

    payload = json.dumps(
        {
            "chat_id": chat_id,
            "text": "Issiqxona Nexus: Telegram ulanishi muvaffaqiyatli tekshirildi.",
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=Config.TELEGRAM_TIMEOUT) as response:
            result = json.loads(response.read().decode("utf-8"))
            if result.get("ok"):
                return True, "Telegramga test xabar yuborildi."
            return False, result.get("description", "Telegram javobi muvaffaqiyatsiz.")
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="ignore")
        return False, f"Telegram HTTP xatosi: {detail or error.reason}"
    except Exception as error:
        return False, f"Telegram ulanish xatosi: {error}"


def send_telegram_message(text, token=None, chat_id=None):
    settings = _telegram_settings()
    token = (token or settings.get("token") or "").strip()
    chat_id = (chat_id or settings.get("chatId") or "").strip()

    if settings and not settings.get("enabled", True):
        return False, "Telegram bildirishnomalari o'chirilgan."

    if not token or not chat_id:
        return False, "Telegram sozlamalari saqlanmagan."

    payload = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=Config.TELEGRAM_TIMEOUT) as response:
            result = json.loads(response.read().decode("utf-8"))
            if result.get("ok"):
                return True, "Telegram xabar yuborildi."
            return False, result.get("description", "Telegram javobi muvaffaqiyatsiz.")
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="ignore")
        return False, f"Telegram HTTP xatosi: {detail or error.reason}"
    except Exception as error:
        return False, f"Telegram ulanish xatosi: {error}"


def notify_device_change(device, enabled):
    names = {
        "fan": "Ventilyator",
        "pump": "Suv nasosi",
        "light": "Ostirish chirogi",
        "camera": "Kamera",
    }
    state = "yoqildi" if enabled else "o'chirildi"
    return send_telegram_message(f"Issiqxona Nexus: {names.get(device, device)} {state}.")
