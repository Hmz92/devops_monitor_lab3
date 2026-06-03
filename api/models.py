from dataclasses import dataclass
from pydantic import BaseModel, Field

@dataclass
class Server:
    id: int
    name: str
    host: str
    port: int
    status: str = "unknown"

    def base_url(self) -> str:
        """Return the base URL of the server."""
        return f"http://{self.host}:{self.port}"


class ServerIn(BaseModel):
    name: str
    host: str
    port: int = Field(..., ge=1, le=65535)


class ServerOut(BaseModel):
    id: int
    name: str
    host: str
    port: int
    status: str

    model_config = {
        "from_attributes": True
    }
