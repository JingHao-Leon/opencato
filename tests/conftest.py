"""pytest 共享环境：必须在任何 app 模块导入前设置好环境变量。"""
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("WECOM_CORP_ID", "wwtest")
os.environ.setdefault("WECOM_AGENT_ID", "1000002")
os.environ.setdefault("WECOM_SECRET", "test_secret")
os.environ.setdefault("WECOM_TOKEN", "tok")
os.environ.setdefault("WECOM_ENCODING_AES_KEY", "jWmYm7qr5nMoAUwZRjGtBxmz3KA1tkAj3ykkR6q2B2C")
os.environ.setdefault("LLM_API_KEY", "sk-test")

_tmpdir = tempfile.mkdtemp(prefix="meowminder-test-")
os.environ["DATABASE_PATH"] = str(Path(_tmpdir) / "test.db")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from app import db


@pytest.fixture(autouse=True)
def fresh_db():
    db.init()
    with db._lock, db._conn:
        db._conn.executescript("DELETE FROM reminders; DELETE FROM checkins; DELETE FROM users;")
    yield
