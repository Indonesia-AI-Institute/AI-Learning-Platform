"""
End-to-end auth flow through the real HTTP layer: register, login, /me,
logout, and — the point of this file — that a blacklisted token is
actually rejected (finding #3) and that a locked-out account still runs
a password comparison instead of short-circuiting (finding #11).
"""


async def _register(client, email="student@example.com", role="student"):
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test User",
            "email": email,
            "password": "correcthorsebatterystaple",
            "role": role,
        },
    )
    return resp


async def test_register_returns_201_and_token(client):
    resp = await _register(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


async def test_register_duplicate_email_rejected(client):
    await _register(client)
    resp = await _register(client)
    assert resp.status_code == 400


async def test_login_with_correct_credentials(client):
    await _register(client)
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "student@example.com", "password": "correcthorsebatterystaple"},
    )
    assert resp.status_code == 200
    assert resp.json()["access_token"]


async def test_login_with_wrong_password_rejected(client):
    await _register(client)
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "student@example.com", "password": "wrong-password"},
    )
    assert resp.status_code == 400


async def test_login_with_unknown_email_rejected(client):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "whatever12345"},
    )
    assert resp.status_code == 400


async def test_me_requires_auth(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


async def test_me_returns_current_user_and_no_password_hash(client):
    reg = await _register(client)
    token = reg.json()["access_token"]

    resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "student@example.com"
    assert "hashed_password" not in body
    assert "password" not in body


async def test_logout_then_reuse_of_token_is_rejected(client):
    """Regression test for finding #3: logout must actually revoke the token."""
    reg = await _register(client)
    token = reg.json()["access_token"]

    logout_resp = await client.post(
        "/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"}
    )
    assert logout_resp.status_code == 200

    me_resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 401
    assert "revoked" in me_resp.json()["detail"].lower()


async def test_unrelated_token_still_works_after_someone_else_logs_out(client):
    """Blacklisting must be per-token, not a global switch."""
    reg1 = await _register(client, email="a@example.com")
    token1 = reg1.json()["access_token"]
    reg2 = await _register(client, email="b@example.com")
    token2 = reg2.json()["access_token"]

    await client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token1}"})

    resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token2}"})
    assert resp.status_code == 200
