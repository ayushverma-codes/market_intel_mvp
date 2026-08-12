import httpx

from app.config import Settings


def send_slack(text: str, settings: Settings) -> bool:
    if not settings.slack_webhook_url:
        return False
    response = httpx.post(settings.slack_webhook_url, json={"text": text}, timeout=10.0)
    response.raise_for_status()
    return True


def send_hitl(payload: dict, settings: Settings) -> bool:
    if not settings.hitl_webhook_url:
        return False
    response = httpx.post(settings.hitl_webhook_url, json=payload, timeout=10.0)
    response.raise_for_status()
    return True
