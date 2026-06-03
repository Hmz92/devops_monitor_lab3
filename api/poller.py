import httpx
import asyncio
import logging

logger = logging.getLogger(__name__)

async def poll_server(server_id: int, url: str, store: dict):
    """Check the health of a single server and update its status in-place.
    
    Status mapping:
      - "UP": HTTP 200
      - "DEGRADED": Any other HTTP status code
      - "DOWN": Connection errors / timeouts
    """
    if server_id not in store:
        return
    server = store[server_id]
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{url}/health")
            if resp.status_code == 200:
                server.status = "UP"
            else:
                server.status = "DEGRADED"
    except (httpx.RequestError, Exception):
        server.status = "DOWN"


async def run_poll_loop(store: dict, interval: int = 10):
    """Infinite loop that polls all servers concurrently and sleeps for the interval."""
    while True:
        try:
            if store:
                tasks = [
                    poll_server(server.id, server.base_url(), store)
                    for server in list(store.values())
                ]
                await asyncio.gather(*tasks)
        except Exception as e:
            logger.error("Error in background poller: %s", e)
        await asyncio.sleep(interval)
