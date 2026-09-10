import sys
from unittest.mock import MagicMock, patch
import pytest

# Mock MySQL BEFORE importing app
mock_mysql = MagicMock()
mock_mysql.connector.connect.return_value = MagicMock()

sys.modules["mysql"] = mock_mysql
sys.modules["mysql.connector"] = mock_mysql.connector

import app

@pytest.fixture
def client():
    app.app.config["TESTING"] = True
    app.app.config["SECRET_KEY"] = "test-secret-key"

    with app.app.test_client() as client:
        yield client


@pytest.fixture
def mock_cursor():
    cursor = MagicMock()
    return cursor


# ============================================================
# allowed_file()
# ============================================================

def test_allowed_file_valid_extensions():
    assert app.allowed_file("image.png") is True
    assert app.allowed_file("image.jpg") is True
    assert app.allowed_file("image.jpeg") is True
    assert app.allowed_file("image.gif") is True
    assert app.allowed_file("video.mp4") is True
    assert app.allowed_file("video.webm") is True


def test_allowed_file_invalid_extensions():
    assert app.allowed_file("document.pdf") is False
    assert app.allowed_file("script.py") is False
    assert app.allowed_file("archive.zip") is False


def test_allowed_file_without_extension():
    assert app.allowed_file("image") is False


def test_allowed_file_case_insensitive():
    assert app.allowed_file("IMAGE.PNG") is True
    assert app.allowed_file("VIDEO.MP4") is True


# ============================================================
# search_posts()
# ============================================================

def test_search_posts_returns_matching_posts(mock_cursor):
    mock_cursor.fetchall.return_value = [
        (1, "Python Tutorial"),
        (2, "Docker Guide"),
        (3, "Python Flask"),
    ]

    with patch.object(app, "cursor", mock_cursor):
        result = app.search_posts("python")

    assert result == {
        "Python Tutorial": 1,
        "Python Flask": 3,
    }


def test_search_posts_is_case_insensitive(mock_cursor):
    mock_cursor.fetchall.return_value = [
        (1, "Python Tutorial"),
        (2, "Docker Guide"),
    ]

    with patch.object(app, "cursor", mock_cursor):
        result = app.search_posts("PYTHON")

    assert result == {
        "Python Tutorial": 1
    }


def test_search_posts_no_results(mock_cursor):
    mock_cursor.fetchall.return_value = [
        (1, "Python Tutorial"),
        (2, "Docker Guide"),
    ]

    with patch.object(app, "cursor", mock_cursor):
        result = app.search_posts("kubernetes")

    assert result == {}


# ============================================================
# is_admin()
# ============================================================

def test_is_admin_true(mock_cursor):
    mock_cursor.fetchone.return_value = (1,)

    with patch.object(app, "cursor", mock_cursor):
        assert app.is_admin("admin") is True


def test_is_admin_false(mock_cursor):
    mock_cursor.fetchone.return_value = (0,)

    with patch.object(app, "cursor", mock_cursor):
        assert app.is_admin("user") is False


def test_is_admin_user_not_found(mock_cursor):
    mock_cursor.fetchone.return_value = None

    with patch.object(app, "cursor", mock_cursor):
        assert app.is_admin("unknown") is False


# ============================================================
# getpost()
# ============================================================

def test_getpost(mock_cursor):
    expected_post = (1, "Test Post", "2026-09-10")

    mock_cursor.fetchone.return_value = expected_post

    with patch.object(app, "cursor", mock_cursor):
        result = app.getpost(1)

    assert result == expected_post
    mock_cursor.execute.assert_called_once()


# ============================================================
# getcomments()
# ============================================================

def test_getcomments(mock_cursor):
    expected_comments = [
        (1, 10, "chirag", "Great post"),
        (2, 10, "user2", "Nice article"),
    ]

    mock_cursor.fetchall.return_value = expected_comments

    with patch.object(app, "cursor", mock_cursor):
        result = app.getcomments(10)

    assert result == expected_comments


# ============================================================
# getpostsections()
# ============================================================

def test_getpostsections(mock_cursor):
    expected_sections = [
        ("heading", "Introduction", None),
        ("text", "Hello world", None),
        ("code", "print('hello')", None),
    ]

    mock_cursor.fetchall.return_value = expected_sections

    with patch.object(app, "cursor", mock_cursor):
        result = app.getpostsections(1)

    assert result == expected_sections


# ============================================================
# get_all_users()
# ============================================================

def test_get_all_users(mock_cursor):
    expected_users = [
        (1, "admin", "admin@example.com", "hashed", 1),
        (2, "user", "user@example.com", "hashed", 0),
    ]

    mock_cursor.fetchall.return_value = expected_users

    with patch.object(app, "cursor", mock_cursor):
        result = app.get_all_users()

    assert result == expected_users


# ============================================================
# get_favourites()
# ============================================================

def test_get_favourites(mock_cursor):
    expected = [
        (1, "Python Tutorial"),
        (3, "Docker Guide"),
    ]

    mock_cursor.fetchall.return_value = expected

    with patch.object(app, "cursor", mock_cursor):
        result = app.get_favourites("chirag")

    assert result == expected


# ============================================================
# Authentication
# ============================================================

def test_auth_existing_user(mock_cursor):
    expected_user = (
        1,
        "chirag",
        "chirag@example.com",
        "hashed-password",
        0,
    )

    mock_cursor.fetchone.return_value = expected_user

    with patch.object(app, "cursor", mock_cursor):
        result = app.auth("chirag@example.com")

    assert result == expected_user


def test_auth_user_not_found(mock_cursor):
    mock_cursor.fetchone.return_value = None

    with patch.object(app, "cursor", mock_cursor):
        result = app.auth("unknown@example.com")

    assert result is None


# ============================================================
# create_user()
# ============================================================

def test_create_user(mock_cursor):
    mock_conn = MagicMock()

    with patch.object(app, "cursor", mock_cursor), \
         patch.object(app, "conn", mock_conn):

        result = app.create_user(
            "chirag",
            "chirag@example.com",
            "hashed-password"
        )

    assert result is None

    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()


# ============================================================
# create_comment()
# ============================================================

def test_create_comment(mock_cursor):
    mock_conn = MagicMock()

    with patch.object(app, "cursor", mock_cursor), \
         patch.object(app, "conn", mock_conn):

        result = app.create_comment(
            10,
            "chirag",
            "Great article!"
        )

    assert result is None
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()


# ============================================================
# Login route
# ============================================================

def test_login_get(client):
    response = client.get("/login")

    assert response.status_code == 200


def test_login_user_not_found(client):
    with patch.object(app, "auth", return_value=None):
        response = client.post(
            "/login",
            data={
                "email": "unknown@example.com",
                "password": "password",
            },
            follow_redirects=False,
        )

    assert response.status_code == 302
    assert "/login" in response.location


def test_login_admin(client):
    user = (
        1,
        "admin",
        "admin@example.com",
        "hashed-password",
        1,
    )

    with patch.object(app, "auth", return_value=user), \
         patch.object(
             app.bcrypt,
             "check_password_hash",
             return_value=True
         ), \
         patch.object(app, "create_user_session"):

        response = client.post(
            "/login",
            data={
                "email": "admin@example.com",
                "password": "password",
            },
        )

    assert response.status_code == 302
    assert "/admin" in response.location


def test_login_normal_user(client):
    user = (
        1,
        "chirag",
        "chirag@example.com",
        "hashed-password",
        0,
    )

    with patch.object(app, "auth", return_value=user), \
         patch.object(
             app.bcrypt,
             "check_password_hash",
             return_value=True
         ), \
         patch.object(app, "create_user_session"):

        response = client.post(
            "/login",
            data={
                "email": "chirag@example.com",
                "password": "password",
            },
        )

    assert response.status_code == 302
    assert "/" in response.location


def test_login_wrong_password(client):
    user = (
        1,
        "chirag",
        "chirag@example.com",
        "hashed-password",
        0,
    )

    with patch.object(app, "auth", return_value=user), \
         patch.object(
             app.bcrypt,
             "check_password_hash",
             return_value=False
         ):

        response = client.post(
            "/login",
            data={
                "email": "chirag@example.com",
                "password": "wrong-password",
            },
        )

    assert response.status_code == 302
    assert "/login" in response.location


# ============================================================
# Logout
# ============================================================

def test_logout(client):
    with client.session_transaction() as session:
        session["current_user"] = {
            "username": "chirag",
            "email": "chirag@example.com",
        }

    response = client.get("/logout")

    assert response.status_code == 302
    assert "/" in response.location

    with client.session_transaction() as session:
        assert "current_user" not in session


# ============================================================
# Signup
# ============================================================

def test_signup_get(client):
    response = client.get("/signup")

    assert response.status_code == 200


def test_signup_existing_email(client):
    with patch.object(
        app,
        "auth",
        return_value=(1, "chirag", "email", "hash", 0)
    ):

        response = client.post(
            "/signup",
            data={
                "username": "newuser",
                "email": "existing@example.com",
                "password": "password",
            },
        )

    assert response.status_code == 302
    assert "/signup" in response.location


def test_signup_existing_username(client):
    with patch.object(app, "auth", return_value=None), \
         patch.object(
             app,
             "checkusername",
             return_value=(1, "existing", "email", "hash", 0)
         ):

        response = client.post(
            "/signup",
            data={
                "username": "existing",
                "email": "new@example.com",
                "password": "password",
            },
        )

    assert response.status_code == 302
    assert "/signup" in response.location


def test_signup_success(client):
    with patch.object(app, "auth", return_value=None), \
         patch.object(app, "checkusername", return_value=None), \
         patch.object(app.verify, "genotp", return_value=123456), \
         patch.object(app.verify, "send_vmail"):

        response = client.post(
            "/signup",
            data={
                "username": "chirag",
                "email": "chirag@example.com",
                "password": "password",
            },
        )

    assert response.status_code == 302
    assert "/signup/verify" in response.location

    with client.session_transaction() as session:
        assert session["verify"]["username"] == "chirag"
        assert session["verify"]["email"] == "chirag@example.com"
        assert session["verify"]["geno"] == 123456


# ============================================================
# OTP verification
# ============================================================

def test_signup_verify_success(client):
    with client.session_transaction() as session:
        session["verify"] = {
            "username": "chirag",
            "email": "chirag@example.com",
            "password": "password",
            "geno": 123456,
        }

    with patch.object(
        app.bcrypt,
        "generate_password_hash"
    ) as mock_hash, \
         patch.object(app, "create_user"):

        mock_hash.return_value.decode.return_value = "hashed-password"

        with patch("app.time.sleep"):
            response = client.post(
                "/signup/verify",
                data={"otp": "123456"},
            )

    assert response.status_code == 302
    assert "/login" in response.location


def test_signup_verify_invalid_otp(client):
    with client.session_transaction() as session:
        session["verify"] = {
            "username": "chirag",
            "email": "chirag@example.com",
            "password": "password",
            "geno": 123456,
        }

    with patch("app.time.sleep"):
        response = client.post(
            "/signup/verify",
            data={"otp": "999999"},
        )

    assert response.status_code == 302
    assert "/signup" in response.location


# ============================================================
# Search API
# ============================================================

def test_search_route(client):
    with patch.object(
        app,
        "search_posts",
        return_value={
            "Python Tutorial": 1,
            "Python Flask": 2,
        },
    ):
        response = client.get("/search?query=python")

    assert response.status_code == 200
    assert response.get_json() == {
        "Python Tutorial": 1,
        "Python Flask": 2,
    }


# ============================================================
# Image route
# ============================================================

def test_image_without_filename(client):
    response = client.get("/image")

    assert response.status_code == 404


def test_image_existing_file(client, tmp_path):
    image = tmp_path / "test.png"
    image.write_bytes(b"fake-image")

    response = client.get(
        "/image",
        query_string={"filename": str(image)}
    )

    assert response.status_code == 200
    assert response.data == b"fake-image"


# ============================================================
# Video route
# ============================================================

def test_video_without_filename(client):
    response = client.get("/video")

    assert response.status_code == 404


def test_video_existing_file(client, tmp_path):
    video = tmp_path / "test.mp4"
    video.write_bytes(b"fake-video")

    response = client.get(
        "/video",
        query_string={"filename": str(video)}
    )

    assert response.status_code == 200
    assert response.data == b"fake-video"


# ============================================================
# 404
# ============================================================

def test_404_page(client):
    response = client.get("/does-not-exist")

    assert response.status_code == 404


# ============================================================
# Favourites
# ============================================================

def test_favourites_requires_login(client):
    response = client.get("/favourites")

    assert response.status_code == 302
    assert "/login" in response.location


def test_favourites_logged_in(client):
    with client.session_transaction() as session:
        session["current_user"] = {
            "username": "chirag"
        }

    with patch.object(
        app,
        "get_favourites",
        return_value=[(1, "Python Tutorial")]
    ):

        response = client.get("/favourites")

    assert response.status_code == 200


def test_add_favourite_requires_login(client):
    response = client.post("/add_favourite/1")

    assert response.status_code == 302


def test_add_favourite_success(client):
    with client.session_transaction() as session:
        session["current_user"] = {
            "username": "chirag"
        }

    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None

    mock_conn = MagicMock()

    with patch.object(app, "cursor", mock_cursor), \
         patch.object(app, "conn", mock_conn):

        response = client.post(
            "/add_favourite/1",
            query_string={"next": "/"}
        )

    assert response.status_code == 302
    assert response.location.endswith("/")

    mock_conn.commit.assert_called_once()


def test_add_existing_favourite(client):
    with client.session_transaction() as session:
        session["current_user"] = {
            "username": "chirag"
        }

    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (
        1,
        "chirag",
        10,
    )

    with patch.object(app, "cursor", mock_cursor):
        response = client.post(
            "/add_favourite/10",
            query_string={"next": "/"}
        )

    assert response.status_code == 302


def test_remove_favourite_requires_login(client):
    response = client.get("/remove_favourite/1")

    assert response.status_code == 302


def test_remove_favourite_success(client):
    with client.session_transaction() as session:
        session["current_user"] = {
            "username": "chirag"
        }

    mock_cursor = MagicMock()
    mock_conn = MagicMock()

    with patch.object(app, "cursor", mock_cursor), \
         patch.object(app, "conn", mock_conn):

        response = client.get(
            "/remove_favourite/1",
            headers={"Referer": "/favourites"}
        )

    assert response.status_code == 302
    mock_conn.commit.assert_called_once()