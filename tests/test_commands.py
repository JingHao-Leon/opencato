"""指令解析测试。"""
import re
from datetime import datetime, timedelta

import pytest

from app import commands, db

USER = "pytest-user"


def test_checkin():
    reply = commands.handle("打卡", USER)
    assert "第 1 次打卡" in reply
    reply = commands.handle("打卡", USER)
    assert "第 1 次打卡" in reply  # 同一天重复打卡不重复计数


def test_plan_empty_and_listed():
    assert "没有待办提醒" in commands.handle("计划", USER)
    commands.handle("30分钟后提醒我喝水", USER)
    reply = commands.handle("计划", USER)
    assert "喝水" in reply


def test_focus():
    reply = commands.handle("开始专注25分钟", USER)
    assert "本喵来叫你" in reply
    rows = db.pending_reminders(USER)
    assert len(rows) == 1 and rows[0]["kind"] == "focus"
    assert abs((datetime.fromisoformat(rows[0]["remind_at"]) - datetime.now()).total_seconds() - 25 * 60) < 5


def test_minutes_later():
    reply = commands.handle("30分钟后提醒我喝水", USER)
    assert "喝水" in reply
    rows = db.pending_reminders(USER)
    assert abs((datetime.fromisoformat(rows[0]["remind_at"]) - datetime.now()).total_seconds() - 30 * 60) < 5


def test_clock_after_order():
    reply = commands.handle("提醒我18:30吃药", USER)
    assert "18:30" in reply and "吃药" in reply
    rows = db.pending_reminders(USER)
    assert rows[0]["remind_at"][11:16] == "18:30"


def test_clock_before_order_tomorrow():
    reply = commands.handle("明天早上8点提醒我开会", USER)
    assert "明天 08:00" in reply
    rows = db.pending_reminders(USER)
    assert rows[0]["remind_at"][:10] == (datetime.now() + timedelta(days=1)).date().isoformat()


def test_clock_half_hour_evening():
    reply = commands.handle("今晚9点半提醒我关电脑", USER)
    assert "21:30" in reply


def test_clock_day_after_tomorrow_afternoon():
    reply = commands.handle("后天下午3点提醒我打电话", USER)
    assert "后天 15:00" in reply
    rows = db.pending_reminders(USER)
    assert rows[0]["remind_at"][:10] == (datetime.now() + timedelta(days=2)).date().isoformat()


def test_past_time_rolls_to_tomorrow():
    earlier = datetime.now() - timedelta(hours=2)
    if earlier.date() != datetime.now().date():
        pytest.skip("凌晨时段跨天，跳过（已过时间仍在今日未来，无法构造）")
    past = earlier.strftime("%H:%M")
    reply = commands.handle(f"提醒我{past}吃药", USER)
    assert "明天" in reply


def test_no_false_positive_without_clock():
    assert commands.handle("提醒我3件事", USER) is None


def test_chat_falls_through():
    assert commands.handle("今天好烦啊", USER) is None
