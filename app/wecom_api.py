"""企业微信服务端 API：access_token 缓存 + 主动发送应用消息。"""
import threading
import time

import requests

from . import config

_BASE = "https://qyapi.weixin.qq.com/cgi-bin"
_token_cache = {"value": None, "expires_at": 0.0}
_lock = threading.Lock()


def _get_access_token() -> str:
    with _lock:
        if _token_cache["value"] and time.time() < _token_cache["expires_at"] - 60:
            return _token_cache["value"]
        resp = requests.get(
            f"{_BASE}/gettoken",
            params={"corpid": config.WECOM_CORP_ID, "corpsecret": config.WECOM_SECRET},
            timeout=10,
        ).json()
        if resp.get("errcode") != 0:
            raise RuntimeError(f"gettoken 失败: {resp}")
        _token_cache["value"] = resp["access_token"]
        _token_cache["expires_at"] = time.time() + resp.get("expires_in", 7200)
        return _token_cache["value"]


def send_text(user_id: str, content: str):
    """向单个成员主动推送应用文本消息。"""
    resp = requests.post(
        f"{_BASE}/message/send",
        params={"access_token": _get_access_token()},
        json={
            "touser": user_id,
            "msgtype": "text",
            "agentid": config.WECOM_AGENT_ID,
            "text": {"content": content},
        },
        timeout=10,
    ).json()
    if resp.get("errcode") != 0:
        raise RuntimeError(f"消息发送失败: {resp}")
    return resp
