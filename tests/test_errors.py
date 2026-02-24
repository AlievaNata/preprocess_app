def test_preprocess_without_data(client):
    response = client.post("/preprocess")
    assert response.status_code == 400


def test_load_invalid_csv(client):
    response = client.post(
        "/load_csv",
        files={"file": ("bad.txt", b"not a csv", "text/plain")}
    )
    assert response.status_code in (400, 422, 500)


def test_invalid_endpoint(client):
    response = client.get("/no_such_endpoint")
    assert response.status_code == 404



