"""Lightweight V-Model API server for testing-validation-platform."""

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

app = FastAPI(title="Testing & Validation Platform - V-Model Dashboard", version="1.0.0")

try:
    from backend.api.routers.vmodel_dashboard import router as vmodel_router
    app.include_router(vmodel_router)
except ImportError:
    @app.get("/api/vmodel/board")
    async def vmodel_fallback():
        return {"error": "V_MODEL_BOARD.md not found. Sync with tracker first."}

@app.get("/")
async def root():
    """Serve V-Model status dashboard."""
    status_path = Path(__file__).parent.parent.parent / "testing-validation-platform" / "vmodel-status.html"
    if status_path.exists():
        return FileResponse(status_path)
    return {"error": "vmodel-status.html not found"}

@app.get("/health")
async def health():
    """Health check."""
    return {"status": "ok", "service": "testing-validation-platform"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8004)
