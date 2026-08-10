"""MeowMinder 入口：企业微信回调 + 提醒引擎。"""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, Request
from fastapi.responses import PlainTextResponse

from . import commands, config, db, llm, scheduler
from .wecom_api import send_text
from .wecom_crypto import WXBizMsgCrypt, WXBizMsgCryptError

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("meowminder")

crypt = WXBizMsgCrypt(config.WECOM_TOKEN, config.WECOM_ENCODING_AES_KEY, config.WECOM_CORP_ID)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init()
    scheduler.start()
    yield


app = FastAPI(title="MeowMinder", version="0.1.0", lifespan=lifespan)


@app.get("/wecom/callback", response_class=PlainTextResponse)
def verify_callback(
    msg_signature: str = Query(...),
    timestamp: str = Query(...),
    nonce: str = Query(...),
    echostr: str = Query(...),
):
    """企业微信后台「保存回调 URL」时的验证请求。"""
    return crypt.verify_url(msg_signature, timestamp, nonce, echostr)


@app.post("/wecom/callback", response_class=PlainTextResponse)
async def receive_callback(
    request: Request,
    msg_signature: str = Query(...),
    timestamp: str = Query(...),
    nonce: str = Query(...),
):
    body = await request.body()
    try:
        msg = crypt.decrypt_message(body, msg_signature, timestamp, nonce)
    except WXBizMsgCryptError as e:
        log.warning("回调解密失败: %s", e)
        return "success"  # 仍回 success，避免企业微信反复重试

    if msg.get("MsgType") == "text":
        # 保留任务强引用，否则协程可能被 GC 提前回收（"Task was destroyed but it is pending"）
        task = asyncio.create_task(_handle_text(msg))
        _background_tasks.add(task)
        task.add_done_callback(_background_tasks.discard)
    return "success"  # 立即响应，回复走主动推送，规避回调超时


_background_tasks: set[asyncio.Task] = set()


async def _handle_text(msg: dict):
    user_id = msg.get("FromUserName", "")
    content = msg.get("Content", "").strip()
    if not user_id or not content:
        return
    db.touch_user(user_id)
    try:
        reply = commands.handle(content, user_id)
        if reply is None:
            reply = await asyncio.to_thread(llm.chat, content)
        await asyncio.to_thread(send_text, user_id, reply)
    except Exception:
        log.exception("消息处理失败 user=%s", user_id)
