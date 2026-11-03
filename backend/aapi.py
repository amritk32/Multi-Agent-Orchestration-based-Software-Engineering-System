import os
from pathlib import Path

from dotenv import load_dotenv


# Load backend/.env once from this module so every API client receives the same
# configuration regardless of the directory used to start the application.
load_dotenv(Path(__file__).with_name(".env"))

OPEN_AI_API = os.getenv("OPEN_AI_API", "").strip()