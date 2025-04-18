def test_healthchecker(client, get_token):
    """Test create contact endpoint

    Args:
        client (_type_): HTTP client
        get_token (_type_): JWT token
    """
    response = client.get("/api/healthchecker")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Welcome to FastAPI!"
