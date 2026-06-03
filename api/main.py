import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware

from api.models import Server, ServerIn, ServerOut
from api.metrics import get_system_metrics
from api.auth import verify_api_key
from api.poller import poll_server, run_poll_loop

# In-memory store
_store: dict[int, Server] = {}
_counter = 0
background_poller_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global background_poller_task
    # Start poller loop task in background
    background_poller_task = asyncio.create_task(run_poll_loop(_store, interval=10))
    yield
    # Cancel task on shutdown
    if background_poller_task:
        background_poller_task.cancel()
        try:
            await background_poller_task
        except asyncio.CancelledError:
            pass

app = FastAPI(title="DevOps Monitoring API", lifespan=lifespan)

# Allow CORS for streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/metrics")
async def metrics():
    return get_system_metrics()

@app.websocket("/ws/metrics")
async def ws_metrics(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            metrics_data = get_system_metrics()
            await websocket.send_json(metrics_data)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass

@app.post("/servers", response_model=ServerOut, status_code=201)
async def register_server(server_in: ServerIn, api_key: str = Depends(verify_api_key)):
    global _counter
    _counter += 1
    server = Server(
        id=_counter,
        name=server_in.name,
        host=server_in.host,
        port=server_in.port,
        status="unknown"
    )
    _store[_counter] = server
    return server

@app.get("/servers", response_model=list[ServerOut])
async def list_servers(status: str | None = None):
    servers = list(_store.values())
    if status:
        return [s for s in servers if s.status.upper() == status.upper()]
    return servers

@app.get("/servers/{server_id}", response_model=ServerOut)
async def get_server(server_id: int):
    if server_id not in _store:
        raise HTTPException(status_code=404, detail="Server not found")
    return _store[server_id]

@app.delete("/servers/{server_id}", status_code=204)
async def delete_server(server_id: int, api_key: str = Depends(verify_api_key)):
    if server_id not in _store:
        raise HTTPException(status_code=404, detail="Server not found")
    del _store[server_id]

@app.post("/servers/{server_id}/check", response_model=ServerOut)
async def check_server_now(server_id: int):
    if server_id not in _store:
        raise HTTPException(status_code=404, detail="Server not found")
    server = _store[server_id]
    await poll_server(server_id, server.base_url(), _store)
    return _store[server_id]
