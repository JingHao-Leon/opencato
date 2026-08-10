import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

WECOM_CORP_ID = os.environ["WECOM_CORP_ID"]
WECOM_AGENT_ID = int(os.environ["WECOM_AGENT_ID"])
WECOM_SECRET = os.environ["WECOM_SECRET"]
WECOM_TOKEN = os.environ["WECOM_TOKEN"]
WECOM_ENCODING_AES_KEY = os.environ["WECOM_ENCODING_AES_KEY"]

LLM_API_KEY = os.environ["LLM_API_KEY"]
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.moonshot.cn/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "kimi-k2-0905-preview")

DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "meowminder.db"))

PERSONA_PATH = BASE_DIR / "prompts" / "cat.md"
