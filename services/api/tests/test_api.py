"""后端接口测试（SQLite 隔离环境，无需真实 PostgreSQL）

运行：cd services/api && .venv/Scripts/python -m pytest tests/test_api.py -q
"""
import asyncio
import os
import tempfile

_DB = os.path.join(tempfile.gettempdir(), "wa_test.db")
if os.path.exists(_DB):
    os.remove(_DB)
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///" + _DB

import httpx  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


def _reset_db():
    async def _r():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(_r())


def api_test(coro):
    _reset_db()
    asyncio.run(coro)


def _client():
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


def test_health():
    async def t():
        async with _client() as c:
            r = await c.get("/api/health")
            assert r.status_code == 200 and r.json() == {"ok": True}

    api_test(t())


def test_register_and_login():
    async def t():
        async with _client() as c:
            r = await c.post("/api/auth/register", json={"email": "a@b.com", "password": "123456", "display_name": "小明"})
            assert r.status_code == 200 and r.json()["display_name"] == "小明"
            token = r.json()["access_token"]
            assert (await c.post("/api/auth/register", json={"email": "a@b.com", "password": "123456"})).status_code == 409
            assert (await c.post("/api/auth/register", json={"email": "abc", "password": "123456"})).status_code == 422
            assert (await c.post("/api/auth/login", json={"email": "a@b.com", "password": "wrong1"})).status_code == 401
            r2 = await c.post("/api/auth/login", json={"email": "A@B.com", "password": "123456"})
            assert r2.status_code == 200 and r2.json()["access_token"]
            me = await c.get("/api/users/me", headers={"Authorization": "Bearer " + token})
            assert me.status_code == 200 and me.json()["email"] == "a@b.com"

    api_test(t())


def test_guest():
    async def t():
        async with _client() as c:
            r = await c.post("/api/auth/guest", json={})
            assert r.status_code == 200 and r.json()["display_name"] == "游客"

    api_test(t())


def test_requires_auth():
    async def t():
        async with _client() as c:
            assert (await c.get("/api/sessions/")).status_code == 401

    api_test(t())


def test_sessions_flow():
    async def t():
        async with _client() as c:
            token = (await c.post("/api/auth/guest", json={})).json()["access_token"]
            h = {"Authorization": "Bearer " + token}
            s = await c.post("/api/sessions/", json={"title": "测试会话"}, headers=h)
            assert s.status_code == 201 and s.json()["title"] == "测试会话"
            sid = s.json()["id"]
            assert len((await c.get("/api/sessions/", headers=h)).json()) == 1
            assert (await c.delete(f"/api/sessions/{sid}", headers=h)).json()["ok"] is True
            assert (await c.get("/api/sessions/", headers=h)).json() == []

    api_test(t())


def test_messages_isolation():
    async def t():
        async with _client() as c:
            ta = (await c.post("/api/auth/guest", json={})).json()["access_token"]
            tb = (await c.post("/api/auth/guest", json={})).json()["access_token"]
            ha = {"Authorization": "Bearer " + ta}
            hb = {"Authorization": "Bearer " + tb}
            sid = (await c.post("/api/sessions/", headers=ha)).json()["id"]
            r = await c.post("/api/chat/stream", json={"session_id": sid, "message": "你好"}, headers=ha)
            assert r.status_code == 200 and "data: " in r.text
            msgs = (await c.get(f"/api/sessions/{sid}/messages", headers=ha)).json()
            assert len(msgs) == 2 and {m["role"] for m in msgs} == {"user", "assistant"}
            assert (await c.get(f"/api/sessions/{sid}/messages", headers=hb)).status_code == 404

    api_test(t())


def test_files_flow():
    async def t():
        async with _client() as c:
            token = (await c.post("/api/auth/guest", json={})).json()["access_token"]
            h = {"Authorization": "Bearer " + token}
            up = await c.post("/api/files/upload", files={"file": ("讲义.txt", "信道容量公式 C=B*log2(1+SNR)".encode(), "text/plain")}, headers=h)
            assert up.status_code == 201 and up.json()["filename"] == "讲义.txt"
            fid = up.json()["id"]
            assert len((await c.get("/api/files/", headers=h)).json()) == 1
            content = await c.get(f"/api/files/{fid}/content", headers=h)
            assert "信道容量" in content.text

    api_test(t())


def test_tasks_flow():
    async def t():
        async with _client() as c:
            token = (await c.post("/api/auth/guest", json={})).json()["access_token"]
            h = {"Authorization": "Bearer " + token}
            tk = await c.post("/api/tasks/", json={"type": "power_opt", "params": {"snr": 20}}, headers=h)
            assert tk.status_code == 201 and tk.json()["status"] == "pending"
            tid = tk.json()["id"]
            up = await c.patch(f"/api/tasks/{tid}", json={"status": "done", "result": {"power": 10}}, headers=h)
            assert up.status_code == 200 and up.json()["status"] == "done" and up.json()["result"] == {"power": 10}
            assert len((await c.get("/api/tasks/", headers=h)).json()) == 1
            assert (await c.get(f"/api/tasks/{tid}", headers=h)).status_code == 200
            assert (await c.delete(f"/api/tasks/{tid}", headers=h)).json()["ok"] is True
            assert (await c.get("/api/tasks/", headers=h)).json() == []

    api_test(t())

def test_text_encoding():
    """GBK 编码的文本文件应正确解码，不出现乱码（Issue #15 文档查看修复）"""

    async def t():
        async with _client() as c:
            token = (await c.post("/api/auth/guest", json={})).json()["access_token"]
            h = {"Authorization": "Bearer " + token}
            gbk = "信道容量公式 C=B*log2(1+SNR)".encode("gbk")
            up = await c.post("/api/files/upload", files={"file": ("中文.txt", gbk, "text/plain")}, headers=h)
            assert up.status_code == 201
            fid = up.json()["id"]
            content = await c.get(f"/api/files/{fid}/content", headers=h)
            assert content.text == "信道容量公式 C=B*log2(1+SNR)"

    api_test(t())