"""企业微信回调消息加解密（WXBizMsgCrypt 精简实现，AES-256-CBC）。"""
import base64
import hashlib
import struct
import xml.etree.ElementTree as ET

from Crypto.Cipher import AES


class WXBizMsgCryptError(Exception):
    pass


class WXBizMsgCrypt:
    def __init__(self, token: str, encoding_aes_key: str, corp_id: str):
        self.token = token
        self.corp_id = corp_id
        key = base64.b64decode(encoding_aes_key + "=")
        if len(key) != 32:
            raise WXBizMsgCryptError("EncodingAESKey 解码后必须为 32 字节")
        self.key = key
        self.iv = key[:16]

    def _signature(self, timestamp: str, nonce: str, encrypt_msg: str) -> str:
        items = "".join(sorted([self.token, timestamp, nonce, encrypt_msg]))
        return hashlib.sha1(items.encode()).hexdigest()

    def _decrypt(self, encrypt_msg: str) -> str:
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        plain = cipher.decrypt(base64.b64decode(encrypt_msg))
        pad = plain[-1]
        content = plain[16:-pad]  # 去掉 16 字节随机串和 PKCS7 填充
        msg_len = struct.unpack(">I", content[:4])[0]
        msg = content[4 : 4 + msg_len]
        receive_id = content[4 + msg_len :].decode()
        if receive_id != self.corp_id:
            raise WXBizMsgCryptError(f"ReceiveID 不匹配: {receive_id}")
        return msg.decode()

    def verify_url(self, msg_signature: str, timestamp: str, nonce: str, echostr: str) -> str:
        """回调 URL 验证：校验签名并解密 echostr。"""
        if self._signature(timestamp, nonce, echostr) != msg_signature:
            raise WXBizMsgCryptError("签名不匹配")
        return self._decrypt(echostr)

    def decrypt_message(self, body: bytes, msg_signature: str, timestamp: str, nonce: str) -> dict:
        """解密回调消息体，返回扁平 dict。"""
        root = ET.fromstring(body)
        encrypt = root.findtext("Encrypt", "")
        if self._signature(timestamp, nonce, encrypt) != msg_signature:
            raise WXBizMsgCryptError("签名不匹配")
        plain_xml = ET.fromstring(self._decrypt(encrypt))
        return {child.tag: (child.text or "") for child in plain_xml}
