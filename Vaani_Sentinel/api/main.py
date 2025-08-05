"""
API Main Module for Vaani Sentinel X
Central API configuration and routing
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import auth, agents

# Create FastAPI app
app = FastAPI(
    title="Vaani Sentinel X API",
    description="Autonomous AI Content Generation and Publishing Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Vaani Sentinel X API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2025-08-02T12:00:00Z",
        "version": "1.0.0"
    }
