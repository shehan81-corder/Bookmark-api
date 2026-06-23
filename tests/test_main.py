def test_register_success(client):
    """Happy path: user can register and gets a token back"""
    response = client.post("/api/auth/register", json={
        "username": "newuser",
        "email": "new@example.com",
        "password": "password123"
    })
    assert response.status_code == 201
    data = response.json()
    assert "token" in data
    assert data["user"]["email"] == "new@example.com"
    assert "password" not in data["user"]


def test_login_wrong_password(client, registered_user):
    """Auth edge case: wrong password returns 401"""
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_create_bookmark_invalid_url(client, auth_headers):
    """Validation edge case: invalid URL returns 422"""
    response = client.post("/api/bookmarks", json={
        "url": "not-a-url",
        "title": "Bad bookmark"
    }, headers=auth_headers)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_cannot_access_other_users_bookmark(client):
    """Ownership scoping: user B cannot see user A's bookmarks"""
    user1 = client.post("/api/auth/register", json={
        "username": "user1",
        "email": "user1@example.com",
        "password": "password123"
    }).json()
    user2 = client.post("/api/auth/register", json={
        "username": "user2",
        "email": "user2@example.com",
        "password": "password123"
    }).json()

    headers1 = {"Authorization": f"Bearer {user1['token']}"}
    headers2 = {"Authorization": f"Bearer {user2['token']}"}

    bookmark = client.post("/api/bookmarks", json={
        "url": "https://example.com",
        "title": "User 1 private bookmark"
    }, headers=headers1).json()

    response = client.get(f"/api/bookmarks/{bookmark['id']}", headers=headers2)
    assert response.status_code == 404


def test_delete_bookmark(client, auth_headers):
    """Happy path: deleted bookmark is no longer accessible"""
    bookmark = client.post("/api/bookmarks", json={
        "url": "https://example.com",
        "title": "To be deleted"
    }, headers=auth_headers).json()

    delete_response = client.delete(
        f"/api/bookmarks/{bookmark['id']}",
        headers=auth_headers
    )
    assert delete_response.status_code == 204

    get_response = client.get(
        f"/api/bookmarks/{bookmark['id']}",
        headers=auth_headers
    )
    assert get_response.status_code == 404
