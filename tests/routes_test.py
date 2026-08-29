def test_index_page(client):
    res = client.get('/')
    assert res.status_code == 200

def test_404(client):
    res = client.get('/random_unknown_path')
    assert res.status_code == 404
