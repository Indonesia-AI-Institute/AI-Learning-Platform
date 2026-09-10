async def test_root_endpoint(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "running"


async def test_health_live(client):
    resp = await client.get("/api/v1/health/live")
    assert resp.status_code == 200
