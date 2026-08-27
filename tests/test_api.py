from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_people_org_scoped():
    resp = client.get("/people", params={"org_id": 1})
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 106
    assert all(p["org_id"] == 1 for p in data["people"])


def test_people_other_org():
    resp = client.get("/people", params={"org_id": 2})
    assert resp.status_code == 200
    assert resp.json()["count"] == 106


def test_tags():
    resp = client.get("/tags", params={"org_id": 1})
    assert resp.status_code == 200
    names = [t["name"] for t in resp.json()["tags"]]
    assert len(names) == 12
    assert "volunteer" in names


def test_static_page_served():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "slim-lite" in resp.text
