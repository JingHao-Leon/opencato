"""定时引擎：后台线程每 20 秒扫描到期提醒并主动推送。"""
import logging
import threading
import time
from datetime import datetime

from . import db, wecom_api

log = logging.getLogger("meowminder.scheduler")

MESSAGES = {
    "reminder": "⏰ 到点啦：{text}",
    "focus": "🍅 {text}！休息 5 分钟，本喵为你骄傲",
}


def _tick():
    for row in db.due_reminders(datetime.now()):
        try:
            template = MESSAGES.get(row["kind"], MESSAGES["reminder"])
            wecom_api.send_text(row["user_id"], template.format(text=row["text"]))
            db.mark_sent(row["id"])
        except Exception:
            log.exception("提醒推送失败 id=%s", row["id"])


def start(interval: int = 20):
    def loop():
        while True:
            try:
                _tick()
            except Exception:
                log.exception("scheduler tick 异常")
            time.sleep(interval)

    thread = threading.Thread(target=loop, daemon=True, name="reminder-scheduler")
    thread.start()
    log.info("提醒引擎已启动，每 %s 秒扫描一次", interval)
    return thread
