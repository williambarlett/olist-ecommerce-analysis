"""Run sql/03_clean_views.sql against data/olist.db to create the clean views."""
import sqlite3
from pathlib import Path

# Find the project folder from this file's location (src/ -> project root),
# so the script works no matter which folder you run it from.
ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "olist.db"
SQL_PATH = ROOT / "sql" / "03_clean_views.sql"

con = sqlite3.connect(DB_PATH)

# executescript() runs a file with several statements in it
# (execute() only runs one statement at a time).
con.executescript(SQL_PATH.read_text(encoding="utf-8"))

# List the views that now exist, and how many rows each returns.
views = con.execute(
    "SELECT name FROM sqlite_master WHERE type = 'view' ORDER BY name"
).fetchall()
for (name,) in views:
    count = con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
    print(f"{name}: {count:,} rows")

con.close()
