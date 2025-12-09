from server.mcp_server import app
from server.utils.config import load_config
import uvicorn


if __name__ == "__main__":
    cfg = load_config()
    uvicorn.run(app, host=cfg.host, port=cfg.port, log_level=cfg.log_level.lower())
