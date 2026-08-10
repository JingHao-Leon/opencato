"""HTTP 端到端 + 调度器测试（外部调用全部 mock）。"""
import asyncio
import base64
import hashlib
import struct
from datetime import datetime, timedelta

from Crypto.Cipher import AES
from fastapi.testclient import TestClient

from app import db, main, scheduler

TOKEN = "tok"
AES_KEY = "jWmYm7qr5nMoAUwZRjGtBxmz3KA1tkAj3ykkR6q2B2C"
CORP = "wwtest"

client = TestClient(main.app)


def _encrypt(plaintext: str) -> str:
    key = base64.b64decode(AES_KEY + "=")
    raw = plaintext.encode()
    blob = b"0123456789abcdef" + struct.pack(">I", len(raw)) + raw + CORP.encode()
    pad = 32 - len(blob) % 32
    blob += bytes([pad]) * pad
    return base64.b64encode(AES.new(key, AES.MODE_CBC, key[:16]).encrypt(blob)).decode()


def _sign(enc: str, ts: str, nonce: str) -> str:
    return hashlib.sha1("".join(sorted([TOKEN, ts, nonce, enc])).encode()).hexdigest()


def test_get_callback_verify():
    echo = _encrypt("hello-meow")
    ts, nonce = "1700000000", "abc"
    resp = client.get(
        "/wecom/callback",
        params={"msg_signature": _sign(echo, ts, nonce), "timestamp": ts, "nonce": nonce, "echostr": echo},
    )
    assert resp.status_code == 200
    assert resp.text == "hello-meow"


def test_post_callback_returns_success_immediately():
    inner = "<xml><FromUserName><![CDATA[tester]]></FromUserName><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[打卡]]></Content></xml>"
    enc = _encrypt(inner)
    ts, nonce = "1700000000", "abc"
    body = f"<xml><ToUserName><![CDATA[{CORP}]]></ToUserName><Encrypt><![CDATA[{enc}]]></Encrypt><AgentID>1</AgentID></xml>"
    resp = client.post(
        "/wecom/callback",
        params={"msg_signature": _sign(enc, ts, nonce), "timestamp": ts, "nonce": nonce},
        content=body,
    )
    assert resp.status_code == 200
    assert resp.text == "success"


def test_handle_text_command_flow(monkeypatch):
    sent = []
    monkeypatch.setattr(main, "send_text", lambda uid, text: sent.append((uid, text)))
    asyncio.run(main._handle_text({"FromUserName": "tester", "Content": "打卡", "MsgType": "text"}))
    assert len(sent) == 1
    assert sent[0][0] == "tester" and "打卡成功" in sent[0][1]


def test_handle_text_chat_flow(monkeypatch):
    sent = []
    monkeypatch.setattr(main, "send_text", lambda uid, text: sent.append((uid, text)))
    monkeypatch.setattr(main.llm, "chat", lambda text: "喵？")
    asyncio.run(main._handle_text({"FromUserName": "tester", "Content": "今天好烦啊", "MsgType": "text"}))
    assert sent == [("tester", "喵？")]


def test_scheduler_pushes_due_reminder(monkeypatch):
    sent = []
    monkeypatch.setattr(scheduler.wecom_api, "send_text", lambda uid, text: sent.append((uid, text)))
    db.add_reminder("tester", "吃药", datetime.now() - timedelta(minutes=1))
    db.add_reminder("tester", "开会", datetime.now() + timedelta(hours=1))
    scheduler._tick()
    assert sent == [("tester", "⏰ 到点啦：吃药")]
    remaining = db.pending_reminders("tester")
    assert len(remaining) == 1 and remaining[0]["text"] == "开会"
