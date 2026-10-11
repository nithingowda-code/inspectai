import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.database.session import engine, Base, SessionLocal, DATA_DIR
from backend.app.services.seed_data import seed_sample_products_and_images

# Import API routers
from backend.app.api.health import router as health_router
from backend.app.api.dashboard import router as dashboard_router
from backend.app.api.products import router as products_router
from backend.app.api.inspections import router as inspections_router
from backend.app.api.model import router as model_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database schema is created
    print("[InspectAI] Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    
    # Seed default sample data if table is empty
    db = SessionLocal()
    try:
        seed_sample_products_and_images(db)
    finally:
        db.close()
        
    yield
    # Shutdown logic if needed
    print("[InspectAI] Server shutting down cleanly.")

app = FastAPI(
    title="InspectAI — Universal AI Quality Inspection API",
    description="Automated optical metrology, deep visual anomaly detection, and reference-bank product inspection API.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount data directory for inspection images, heatmaps, references and reports
os.makedirs(DATA_DIR, exist_ok=True)
app.mount("/data", StaticFiles(directory=DATA_DIR), name="data")

# Register routers under /api
app.include_router(health_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(products_router, prefix="/api")
app.include_router(inspections_router, prefix="/api")
app.include_router(model_router, prefix="/api")

@app.get("/")
def root():
    return {
        "message": "InspectAI — Universal AI Quality Inspection API is running.",
        "documentation": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
