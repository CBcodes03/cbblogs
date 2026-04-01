import os
import tempfile
import pytest
import sqlite3
from app import app as flask_app   # ← FIXED IMPORT

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    flask_app.config['DATABASE'] = db_path
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False

    # Create tables for tests
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, email TEXT, password TEXT)")
    cur.execute("CREATE TABLE posts (id INTEGER PRIMARY KEY, title TEXT)")
    cur.execute("""CREATE TABLE post_sections (
                        id INTEGER PRIMARY KEY,
                        post_id INTEGER,
                        section_type TEXT,
                        content TEXT,
                        file_path TEXT,
                        position INTEGER
                   )""")
    cur.execute("""CREATE TABLE comments (
                        id INTEGER PRIMARY KEY, 
                        pid INTEGER, 
                        username TEXT, 
                        body TEXT
                   )""")

    conn.commit()
    conn.close()

    yield flask_app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()
