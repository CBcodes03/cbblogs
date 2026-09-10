import os
import tempfile
import sqlite3
import pytest

from app import app as flask_app


@pytest.fixture
def app(monkeypatch):
    db_fd, db_path = tempfile.mkstemp(suffix=".db")

    # Redirect sqlite3.connect() to the test database
    original_connect = sqlite3.connect

    def test_db_connect(*args, **kwargs):
        return original_connect(db_path, **kwargs)

    monkeypatch.setattr(sqlite3, "connect", test_db_connect)

    flask_app.config["TESTING"] = True
    flask_app.config["WTF_CSRF_ENABLED"] = False

    # Create test database
    conn = sqlite3.connect(db_path)

    conn.executescript("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            email TEXT,
            password TEXT
        );

        CREATE TABLE posts (
            id INTEGER PRIMARY KEY,
            title TEXT
        );

        CREATE TABLE post_sections (
            id INTEGER PRIMARY KEY,
            post_id INTEGER,
            section_type TEXT,
            content TEXT,
            file_path TEXT,
            position INTEGER
        );

        CREATE TABLE comments (
            id INTEGER PRIMARY KEY,
            pid INTEGER,
            username TEXT,
            body TEXT
        );
    """)

    conn.commit()
    conn.close()

    yield flask_app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()
