import os
import tempfile
import sqlite3
import pytest

from app import app as flask_app


@pytest.fixture
def app():
    # Create temporary SQLite database
    db_fd, db_path = tempfile.mkstemp(suffix=".db")

    flask_app.config["DATABASE"] = db_path
    flask_app.config["TESTING"] = True
    flask_app.config["WTF_CSRF_ENABLED"] = False

    # Connect to SQLite test database
    conn = sqlite3.connect(db_path)

    # Create tables
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

    # Cleanup test database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()
