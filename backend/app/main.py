# ... existing imports ...
from fastapi import FastAPI
from backend.app.api.routes import targets
from backend.app.core.database import Base, engine
from backend.app.api.routes import scans
from backend.app.models.scan import Scan
from fastapi.middleware.cors import CORSMiddleware
from backend.app.models.finding import Finding
from backend.app.api.routes import findings
from backend.app.api.routes import reports
from backend.app.models.user import User
from backend.app.api.routes import auth

# Create tables automatically (Simple method for dev)
Base.metadata.create_all(bind=engine)

# Create FastAPI app instance
app = FastAPI()

# Register Router
app.include_router(targets.router, prefix="/api/v1/targets", tags=["Targets"])
app.include_router(scans.router, prefix="/api/v1/scans", tags=["Scans"])
app.include_router(findings.router, prefix="/api/v1/findings", tags=["Findings"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <-- Allow ANY origin (Fixes the 405 error)
    allow_credentials=True,
    allow_methods=["*"],  # <-- Allow ANY method (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # <-- Allow ANY header
)
