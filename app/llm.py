"""LLM 闲聊：OpenAI 兼容接口 + 猫设 system prompt。"""
import requests

from . import config

_persona_cache: str | None = None


def _persona() -> str:
    global _persona_cache
    if _persona_cache is None:
        _persona_cache = config.PERSONA_PATH.read_text(encoding="utf-8")
    return _persona_cache


def chat(user_text: str) -> str:
    resp = requests.post(
        f"{config.LLM_BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {config.LLM_API_KEY}"},
        json={
            "model": config.LLM_MODEL,
            "messages": [
                {"role": "system", "content": _persona()},
                {"role": "user", "content": user_text},
            ],
            "temperature": 0.8,
            "max_tokens": 300,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()
