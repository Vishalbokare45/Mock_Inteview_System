import os
import sqlite3
import uuid
from pathlib import Path


class Database:
    def __init__(self):
        self.path = os.getenv("DATABASE_PATH", "data/app.db")
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.path)

    def _init_db(self):
        with self._connect() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )""")
            conn.execute("""CREATE TABLE IF NOT EXISTS resumes (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                path TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )""")
            conn.execute("""CREATE TABLE IF NOT EXISTS interviews (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                resume_id TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )""")

    def create_user(self, email, password_hash):
        user_id = str(uuid.uuid4())
        with self._connect() as conn:
            conn.execute("INSERT INTO users(id,email,password_hash) VALUES(?,?,?)", (user_id, email, password_hash))
        return self.get_user(user_id)

    def get_user(self, user_id):
        with self._connect() as conn:
            row = conn.execute("SELECT id,email,password_hash,created_at FROM users WHERE id=?", (user_id,)).fetchone()
        return self._user(row) if row else None

    def get_user_by_email(self, email):
        with self._connect() as conn:
            row = conn.execute("SELECT id,email,password_hash,created_at FROM users WHERE email=?", (email,)).fetchone()
        return self._user(row) if row else None

    def create_resume(self, user_id, filename, path):
        resume_id = str(uuid.uuid4())
        with self._connect() as conn:
            conn.execute("INSERT INTO resumes(id,user_id,filename,path) VALUES(?,?,?,?)", (resume_id, user_id, filename, path))
        return resume_id

    def create_interview(self, user_id, resume_id):
        interview_id = str(uuid.uuid4())
        with self._connect() as conn:
            conn.execute("INSERT INTO interviews(id,user_id,resume_id) VALUES(?,?,?)", (interview_id, user_id, resume_id))
        return interview_id

    def interview_belongs_to_user(self, interview_id, user_id):
        with self._connect() as conn:
            row = conn.execute("SELECT 1 FROM interviews WHERE id=? AND user_id=?", (interview_id, user_id)).fetchone()
        return row is not None

    @staticmethod
    def _user(row):
        return {"id": row[0], "email": row[1], "password_hash": row[2], "created_at": row[3]}
