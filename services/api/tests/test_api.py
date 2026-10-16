"""Tests: auth, sessions, projects, tasks + unified status & permission."""
import asyncio
import uuid

from services.worker import wag_runner


def _register(client, email):
    r = client.post(
        "/api/auth/register",
        json={"email": email, "password": "secret123", "display_name": "Tester"},
    )
    assert r.status_code == 201, r.text
    return r.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _email():
    return f"u{uuid.uuid4().hex[:10]}@example.com"


def test_health_and_auth_flow(client):
    assert client.get("/api/health").json()["status"] == "ok"

    email = _email()
    token = _register(client, email)

    r = client.post("/api/auth/login", json={"email": email, "password": "secret123"})
    assert r.status_code == 200
    assert r.json()["user_id"]

    r = client.post("/api/auth/guest")
    assert r.status_code == 200
    assert r.json()["access_token"]

    r = client.post("/api/auth/login", json={"email": email, "password": "wrong"})
    assert r.status_code == 401


def test_requires_token(client):
    assert client.get("/api/sessions/").status_code == 401
    assert client.get("/api/projects").status_code == 401
    assert client.get("/api/tasks").status_code == 401


def test_session_crud_and_message_count(client):
    token = _register(client, _email())

    r = client.post("/api/sessions/", headers=_auth(token))
    assert r.status_code == 201
    sid = r.json()["id"]
    assert r.json()["message_count"] == 0
    assert r.json()["title"] == "New Chat"

    r = client.get("/api/sessions/", headers=_auth(token))
    assert any(s["id"] == sid for s in r.json())

    r = client.get(f"/api/sessions/{sid}/messages", headers=_auth(token))
    assert r.status_code == 200
    assert r.json() == []

    assert client.delete(f"/api/sessions/{sid}", headers=_auth(token)).json()["ok"] is True
    assert client.get(f"/api/sessions/{sid}/messages", headers=_auth(token)).status_code == 404


def test_project_crud(client):
    token = _register(client, _email())

    r = client.post("/api/projects", json={"name": "我的项目", "description": "desc"}, headers=_auth(token))
    assert r.status_code == 201
    pid = r.json()["id"]
    assert r.json()["name"] == "我的项目"

    assert any(p["id"] == pid for p in client.get("/api/projects", headers=_auth(token)).json())
    assert client.get(f"/api/projects/{pid}", headers=_auth(token)).json()["id"] == pid

    r = client.patch(f"/api/projects/{pid}", json={"name": "新名字"}, headers=_auth(token))
    assert r.json()["name"] == "新名字"

    assert client.post("/api/projects", json={"name": "  "}, headers=_auth(token)).status_code == 422

    assert client.delete(f"/api/projects/{pid}", headers=_auth(token)).json()["ok"] is True
    assert client.get(f"/api/projects/{pid}", headers=_auth(token)).status_code == 404


def test_permission_isolation(client):
    token_a = _register(client, _email())
    token_b = _register(client, _email())

    pid = client.post("/api/projects", json={"name": "A项目"}, headers=_auth(token_a)).json()["id"]
    sid = client.post("/api/sessions/", headers=_auth(token_a)).json()["id"]
    tid = client.post("/api/tasks", json={"type": "demo_echo"}, headers=_auth(token_a)).json()["id"]

    assert client.get(f"/api/projects/{pid}", headers=_auth(token_b)).status_code == 404
    assert client.get(f"/api/sessions/{sid}/messages", headers=_auth(token_b)).status_code == 404
    assert client.get(f"/api/tasks/{tid}", headers=_auth(token_b)).status_code == 404

    assert client.get(f"/api/projects/{pid}", headers=_auth(token_a)).status_code == 200


def test_task_lifecycle_and_worker(client):
    token = _register(client, _email())

    r = client.post("/api/tasks", json={"type": "demo_echo", "parameters": {"x": 1}}, headers=_auth(token))
    assert r.status_code == 201
    tid = r.json()["id"]
    assert r.json()["status"] == "queued"

    for _ in range(30):
        if not asyncio.run(wag_runner.run_once()):
            break
        t = client.get(f"/api/tasks/{tid}", headers=_auth(token)).json()
        if t["status"] in ("succeeded", "failed", "cancelled"):
            break

    t = client.get(f"/api/tasks/{tid}", headers=_auth(token)).json()
    assert t["status"] == "succeeded"
    assert t["progress"] == 100
    assert t["result"]["echo"] == {"x": 1}


def test_task_cancel(client):
    token = _register(client, _email())

    tid = client.post("/api/tasks", json={"type": "demo_echo"}, headers=_auth(token)).json()["id"]
    r = client.post(f"/api/tasks/{tid}/cancel", headers=_auth(token))
    assert r.status_code == 200
    assert r.json()["status"] == "cancelled"

    assert client.post(f"/api/tasks/{tid}/cancel", headers=_auth(token)).status_code == 409


def test_task_and_session_attach_to_project(client):
    token = _register(client, _email())

    pid = client.post("/api/projects", json={"name": "P"}, headers=_auth(token)).json()["id"]

    tid = client.post("/api/tasks", json={"type": "demo_echo", "project_id": pid}, headers=_auth(token)).json()["id"]
    assert client.get(f"/api/tasks/{tid}", headers=_auth(token)).json()["project_id"] == pid

    sid = client.post("/api/sessions/", json={"project_id": pid}, headers=_auth(token)).json()["id"]
    assert client.get("/api/sessions/", headers=_auth(token)).json()[0]["project_id"] == pid