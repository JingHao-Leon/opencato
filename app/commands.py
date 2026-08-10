"""指令解析：提醒 / 专注 / 打卡 / 计划。解析失败返回 None，交给 LLM 闲聊。"""
import re
from datetime import datetime, timedelta

from . import db

_DAYS = {"明天": 1, "后天": 2}
_PERIODS = "早上|上午|中午|下午|晚上|凌晨"
_CLOCK_REQ = r"(?P<h>\d{1,2})(?:(?:[:：点])(?P<m>\d{1,2})分?|点半|点)"  # 必须含 点/:/半
_CLOCK_OPT = r"(?P<h>\d{1,2})(?:(?:[:：点])(?P<m>\d{1,2})分?|点半|点)?"  # 时刻部分可省略

# 语序一：(明天)?(时段)?(时刻)提醒我<事项>
_P_BEFORE = re.compile(
    rf"(?P<day>明天|后天)?\s*(?P<period>{_PERIODS})?\s*{_CLOCK_REQ}\s*提醒我\s*(?P<thing>\S.*)"
)
# 语序二：提醒我(明天)?(时段)?(时刻)<事项>（时刻必须带 点/:/半，防止「提醒我3件事」误判）
_P_AFTER = re.compile(
    rf"提醒我\s*(?P<day>明天|后天)?\s*(?P<period>{_PERIODS})?\s*{_CLOCK_REQ}\s*(?P<thing>\S.*)"
)


def _extract_clock(m: re.Match) -> tuple[int, str | None, int, int, str] | None:
    hour = int(m.group("h"))
    if m.group("m") is not None:
        minute = int(m.group("m"))
    elif "点半" in m.group(0):
        minute = 30
    else:
        minute = 0
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None
    thing = m.group("thing").strip(" ，。")
    if not thing:
        return None
    return _DAYS.get(m.group("day"), 0), m.group("period"), hour, minute, thing


def _resolve_clock(day_shift: int, period: str | None, hour: int, minute: int) -> datetime:
    if period in ("下午", "晚上") and hour < 12:
        hour += 12
    if period == "中午" and hour < 11:
        hour += 12
    target = (datetime.now() + timedelta(days=day_shift)).replace(
        hour=hour, minute=minute, second=0, microsecond=0
    )
    # 没指定"明天"且时间已过 → 顺延到明天
    if day_shift == 0 and target <= datetime.now():
        target += timedelta(days=1)
    return target


def _fmt(dt: datetime) -> str:
    delta = (dt.date() - datetime.now().date()).days
    label = {0: "", 1: "明天 ", 2: "后天 "}.get(delta, dt.strftime("%m月%d日 "))
    return f"{label}{dt.strftime('%H:%M')}"


def handle(text: str, user_id: str) -> str | None:
    """命中指令返回回复文案；未命中返回 None。"""
    text = text.strip()

    # 打卡
    if text in ("打卡", "今日打卡"):
        n = db.checkin(user_id)
        return f"打卡成功！这是你的第 {n} 次打卡，继续保持喵 🐾"

    # 计划列表
    if text in ("计划", "提醒", "我的计划", "提醒列表"):
        rows = db.pending_reminders(user_id)
        if not rows:
            return "目前没有待办提醒，说一声「提醒我 18:30 吃药」就行喵"
        lines = [f"· {r['remind_at'][5:16]} {r['text']}" for r in rows[:10]]
        return "你的待办提醒 🐾\n" + "\n".join(lines)

    # 专注
    m = re.search(r"开始?专注\s*(\d+)\s*分钟?", text)
    if m:
        minutes = int(m.group(1))
        end = datetime.now() + timedelta(minutes=minutes)
        db.add_reminder(user_id, f"专注结束（{minutes} 分钟）", end, kind="focus")
        return f"好，{_fmt(end)} 本喵来叫你。手机放下，开冲！🍅"

    # N 分钟后提醒
    m = re.search(r"(\d+)\s*分钟后?提醒我(.+)", text)
    if m:
        target = datetime.now() + timedelta(minutes=int(m.group(1)))
        thing = m.group(2).strip(" ，。")
        db.add_reminder(user_id, thing, target)
        return f"记下了，{_fmt(target)} 提醒你「{thing}」⏰"

    # 时间点提醒（两种语序：「明天早上8点提醒我开会」/「提醒我 18:30 吃药」）
    normalized = text.replace("明晚", "明天晚上").replace("今晚", "晚上")
    for pattern in (_P_BEFORE, _P_AFTER):
        m = pattern.search(normalized)
        if not m:
            continue
        parsed = _extract_clock(m)
        if parsed is None:
            continue
        day_shift, period, hour, minute, thing = parsed
        target = _resolve_clock(day_shift, period, hour, minute)
        db.add_reminder(user_id, thing, target)
        return f"记下了，{_fmt(target)} 提醒你「{thing}」⏰"

    return None
