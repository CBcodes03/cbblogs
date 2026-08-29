import sqlite3

def test_login_page(client):
    res = client.get('/login')
    assert res.status_code == 200

def test_login_user_not_found(client):
    res = client.post('/login', data={"email": "unknown@test.com", "password": "abc"}, follow_redirects=True)
    assert b"user not found" in res.data

def test_signup_page(client):
    res = client.get('/signup')
    assert res.status_code == 200


def test_logout(client):
    with client.session_transaction() as sess:
        sess['current_user'] = {"username": "test"}

    res = client.get('/logout', follow_redirects=True)
    assert res.status_code == 200
