from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from backend.api.routers import domains, sessions, market, financials, risk, export
from backend.core.config import BASE_DIR

# Create FastAPI app
app = FastAPI(
    title="Business Dev Platform",
    description="Wizard-driven business plan generator for German startups",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(domains.router)
app.include_router(sessions.router)
app.include_router(market.router)
app.include_router(financials.router)
app.include_router(risk.router)
app.include_router(export.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/version")
async def get_version():
    """Get API version."""
    return {"version": "1.0.0"}


# Serve frontend
@app.get("/")
async def root():
    """Serve the index.html file."""
    frontend_path = BASE_DIR / "frontend" / "index.html"
    if frontend_path.exists():
        return FileResponse(frontend_path)
    return {"message": "Frontend not yet available"}


# Mount static files for frontend
frontend_dir = BASE_DIR / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
