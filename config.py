import os
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()

UPLOAD_BASE_DIR = Path("uploads")
UPLOAD_BASE_DIR.mkdir(exist_ok=True)
SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
DATABASE_URL = os.getenv("DATABASE_URL", "")
IN_PRODUCTION = eval(os.getenv("IN_PRODUCTOIN", "False"))
TEMPLATES_DIR = Path("templates")
TEMPLATES_DIR.mkdir(exist_ok=True)