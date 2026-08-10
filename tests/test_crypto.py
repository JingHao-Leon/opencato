"""企业微信回调加解密测试。"""
import base64
import hashlib
import struct

import pytest
from Crypto.Cipher import AES

from app.wecom_crypto import WXBizMsgCrypt, WXBizMsgCryptError

TOKEN = "tok"
AES_KEY = "jWmYm7qr5nMoAUwZRjGtBxmz3KA1tkAj3ykkR6q2B2C"
CORP = "wwtest"


def _encrypt(plaintext: str) -> str:
    """按企业微信规范构造密文（测试用，与 _decrypt 互逆）。"""
    key = base64.b64decode(AES_KEY + "=")
    raw = plaintext.encode()
    blob = b"0123456789abcdef" + struct.pack(">I", len(raw)) + raw + CORP.encode()
    pad = 32 - len(blob) % 32
    blob += bytes([pad]) * pad
    return base64.b64encode(AES.new(key, AES.MODE_CBC, key[:16]).encrypt(blob)).decode()


def _sign(enc: str, ts: str, nonce: str) -> str:
    return hashlib.sha1("".join(sorted([TOKEN, ts, nonce, enc])).encode()).hexdigest()


@pytest.fixture
def crypt():
    return WXBizMsgCrypt(TOKEN, AES_KEY, CORP)


def test_verify_url_roundtrip(crypt):
    msg = "<xml><FromUserName><![CDATA[tester]]></FromUserName></xml>"
    enc = _encrypt(msg)
    ts, nonce = "1700000000", "abc"
    assert crypt.verify_url(_sign(enc, ts, nonce), ts, nonce, enc) == msg


def test_verify_url_rejects_bad_signature(crypt):
    enc = _encrypt("hello")
    with pytest.raises(WXBizMsgCryptError):
        crypt.verify_url("bad_signature", "1700000000", "abc", enc)


def test_decrypt_message(crypt):
    msg = "<xml><FromUserName><![CDATA[tester]]></FromUserName><Content><![CDATA[打卡]]></Content></xml>"
    enc = _encrypt(msg)
    ts, nonce = "1700000000", "abc"
    body = (
        f"<xml><ToUserName><![CDATA[{CORP}]]></ToUserName>"
        f"<Encrypt><![CDATA[{enc}]]></Encrypt><AgentID>1</AgentID></xml>"
    ).encode()
    parsed = crypt.decrypt_message(body, _sign(enc, ts, nonce), ts, nonce)
    assert parsed["FromUserName"] == "tester"
    assert parsed["Content"] == "打卡"


def test_decrypt_rejects_wrong_corp(crypt):
    other = WXBizMsgCrypt(TOKEN, AES_KEY, "ww-other-corp")
    enc = _encrypt("hi")
    ts, nonce = "1700000000", "abc"
    body = f"<xml><Encrypt><![CDATA[{enc}]]></Encrypt></xml>".encode()
    with pytest.raises(WXBizMsgCryptError):
        other.decrypt_message(body, _sign(enc, ts, nonce), ts, nonce)
