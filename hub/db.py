"""Hub SQLite DB (imports, logs, activity, students)."""
import sqlite3, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "hub" / "hub.db"


def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    db.executescript("""
    CREATE TABLE IF NOT EXISTS imports (id TEXT PRIMARY KEY, ocw_url TEXT, status TEXT,
                                        stage TEXT, log TEXT, ts REAL);
    CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, level TEXT, msg TEXT);
    CREATE TABLE IF NOT EXISTS activity (id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL,
                                         student TEXT, event TEXT);
    CREATE TABLE IF NOT EXISTS students (id TEXT PRIMARY KEY, name TEXT, cohort TEXT,
                                         masteries TEXT, progress_code TEXT, ts REAL);
    """)
    db.commit()
    return db


def log(msg, level="INFO"):
    db = connect()
    db.execute("INSERT INTO logs(ts,level,msg) VALUES(?,?,?)", (time.time(), level, msg))
    db.commit(); db.close()


def log_line(db, msg, level="INFO"):
    db.execute("INSERT INTO logs(ts,level,msg) VALUES(?,?,?)", (time.time(), level, msg))
    db.commit()
