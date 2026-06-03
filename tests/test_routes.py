from fastapi.testclient import TestClient
import pytest
from api.main import app

def test_get_health():
    """Test public health endpoint."""
    with TestClient(app) as client:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

def test_get_metrics():
    """Test public metrics endpoint."""
    with TestClient(app) as client:
        resp = client.get("/metrics")
        assert resp.status_code == 200
        data = resp.json()
        assert "cpu_percent" in data
        assert "memory_percent" in data
        assert "disk_percent" in data

def test_post_server_no_auth():
    """Test register endpoint fails without key."""
    with TestClient(app) as client:
        payload = {"name": "test-server", "host": "127.0.0.1", "port": 80}
        resp = client.post("/servers", json=payload)
        assert resp.status_code == 403

def test_post_server_invalid_auth():
    """Test register endpoint fails with invalid key."""
    with TestClient(app) as client:
        payload = {"name": "test-server", "host": "127.0.0.1", "port": 80}
        resp = client.post("/servers", json=payload, headers={"X-API-Key": "wrong-key"})
        assert resp.status_code == 403

def test_server_crud_flow():
    """Test full server CRUD registration, listing, checking, and deletion flow."""
    with TestClient(app) as client:
        # 1. Post a valid server with authentication
        payload = {"name": "test-server", "host": "localhost", "port": 8080}
        headers = {"X-API-Key": "demo-key"}
        resp = client.post("/servers", json=payload, headers=headers)
        assert resp.status_code == 201
        
        server = resp.json()
        assert server["id"] is not None
        assert server["name"] == "test-server"
        assert server["status"] == "unknown"
        server_id = server["id"]
        
        # 2. Get server list and see it
        resp = client.get("/servers")
        assert resp.status_code == 200
        servers = resp.json()
        assert any(s["id"] == server_id for s in servers)
        
        # 3. Get single server
        resp = client.get(f"/servers/{server_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "test-server"
        
        # 4. Trigger check (should resolve to DOWN since localhost:8080 is inactive)
        resp = client.post(f"/servers/{server_id}/check")
        assert resp.status_code == 200
        assert resp.json()["status"] == "DOWN"
        
        # 5. Delete server
        resp = client.delete(f"/servers/{server_id}", headers=headers)
        assert resp.status_code == 204
        
        # 6. Verify 404 after deletion
        resp = client.get(f"/servers/{server_id}")
        assert resp.status_code == 404

def test_get_nonexistent_server():
    """Test get endpoint returns 404 for unknown server."""
    with TestClient(app) as client:
        resp = client.get("/servers/9999")
        assert resp.status_code == 404

def test_delete_nonexistent_server():
    """Test delete endpoint returns 404 for unknown server."""
    with TestClient(app) as client:
        headers = {"X-API-Key": "demo-key"}
        resp = client.delete("/servers/9999", headers=headers)
        assert resp.status_code == 404
