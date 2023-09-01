import os
from pathlib import Path

if _dir := os.environ.get("I_HATE_PAPERS_CACHE_DIR"):
    CACHE_DIR = Path(_dir)
else:
    CACHE_DIR = Path("~/.cache").expanduser() / "i-hate-papers"
