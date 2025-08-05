"""
Vaani Sentinel X - Main FastAPI Application
Production-level AI-integrated voice-first platform
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

# Import routers
from api.routers import (
    auth,
    content,
    agents,
    analytics,
    multilingual,
    security
)

# Import database
from core.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    pass

# Initialize FastAPI app
app = FastAPI(
    title="Vaani Sentinel X",
    description="AI-integrated voice-first platform for autonomous content generation and publishing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(content.router, prefix="/api/v1/content", tags=["Content Management"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["AI Agents"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(multilingual.router, prefix="/api/v1/multilingual", tags=["Multilingual"])
app.include_router(security.router, prefix="/api/v1/security", tags=["Security"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Vaani Sentinel X",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2025-01-02T00:00:00Z",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )
