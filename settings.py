from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

ASSISTANT_NAME = "Marvin"
MODEL = "openai/gpt-oss-120b"
MAX_MESSAGES = 20

DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)


WORKSPACE = DATA / "workspace"
NOTES_FILE = DATA / "Note.txt"
DB_FILE = DATA / "Marvin_database.db"
CHROMA_DIR = DATA / "Marvin_chroma"
TOKEN_FILE = DATA / "token.json"
CREDENTIALS_FILE = ROOT / "credentials.json"

WAKE_MODEL = "hey_marvin_v0.1.onnx"
WAKE_THRESHOLD = 0.4
DEFAULT_CITY = "" 