"""
Regression tests for finding #2 (CRITICAL): /chat/direct/* used to have no
auth check at all, letting anyone run unlimited, anonymous LLM calls.
"""


async def _register(client, email="student@example.com"):
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test User",
            "email": email,
            "password": "correcthorsebatterystaple",
            "role": "student",
        },
    )
    return resp.json()["access_token"]


async def test_direct_generate_requires_auth(client):
    resp = await client.post(
        "/api/v1/chat/direct/generate",
        json={"messages": [{"role": "user", "content": "hi"}]},
    )
    assert resp.status_code == 401


async def test_direct_stream_requires_auth(client):
    resp = await client.post(
        "/api/v1/chat/direct/stream",
        json={"messages": [{"role": "user", "content": "hi"}]},
    )
    assert resp.status_code == 401


async def test_direct_generate_rejects_invalid_token(client):
    resp = await client.post(
        "/api/v1/chat/direct/generate",
        json={"messages": [{"role": "user", "content": "hi"}]},
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert resp.status_code == 401


async def test_direct_generate_rejects_blacklisted_token(client):
    token = await _register(client)
    await client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})

    resp = await client.post(
        "/api/v1/chat/direct/generate",
        json={"messages": [{"role": "user", "content": "hi"}]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 401
