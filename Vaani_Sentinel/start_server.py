"""
Startup script for Vaani Sentinel X
Handles initialization, database setup, and server startup
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "fastapi", "uvicorn", "sqlalchemy", "google-generativeai", 
        "groq", "langdetect", "gtts", "better-profanity", "textblob",
        "cryptography", "python-jose", "passlib"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("📦 Installing missing packages...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install"
            ] + missing_packages)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False
    else:
        print("✅ All dependencies are installed")
    
    return True

def check_environment():
    """Check environment configuration"""
    print("🔧 Checking environment configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    # Check required environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        "GOOGLE_GEMINI_API_KEY",
        "GROQ_API_KEY",
        "SECRET_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment configuration is valid")
    return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating necessary directories...")
    
    directories = [
        "content/raw",
        "content/structured", 
        "content/content_ready",
        "content/content_ready/audio",
        "content/multilingual_ready",
        "logs",
        "logs/security",
        "analytics_db",
        "scheduler_db",
        "archives",
        "archives/encrypted_en",
        "archives/encrypted_hi",
        "archives/encrypted_sa",
        "temp",
        "config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created successfully")

async def initialize_database():
    """Initialize the database"""
    print("🗄️ Initializing database...")
    
    try:
        from core.database import init_db
        await init_db()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def check_api_keys():
    """Verify API keys are working"""
    print("🔑 Verifying API keys...")
    
    try:
        # Test Gemini API
        import google.generativeai as genai
        from core.config import settings
        
        genai.configure(api_key=settings.google_gemini_api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Simple test
        response = model.generate_content("Hello")
        if response.text:
            print("✅ Gemini API key is working")
        else:
            print("⚠️ Gemini API key may have issues")
        
        # Test Groq API
        from groq import Groq
        groq_client = Groq(api_key=settings.groq_api_key)
        
        # Simple test
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": "Hello"}],
            model="mixtral-8x7b-32768",
            max_tokens=10
        )
        
        if response.choices[0].message.content:
            print("✅ Groq API key is working")
        else:
            print("⚠️ Groq API key may have issues")
        
        return True
        
    except Exception as e:
        print(f"⚠️ API key verification failed: {e}")
        print("🔄 Server will start but AI features may not work properly")
        return False

def start_server(host="0.0.0.0", port=8000, reload=True):
    """Start the FastAPI server"""
    print(f"🚀 Starting Vaani Sentinel X server on {host}:{port}")
    
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server startup failed: {e}")

async def main():
    """Main startup function"""
    print("=" * 60)
    print("🎯 VAANI SENTINEL X - STARTUP SEQUENCE")
    print("=" * 60)
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed. Exiting.")
        sys.exit(1)
    
    # Step 2: Check environment
    if not check_environment():
        print("❌ Environment check failed. Exiting.")
        sys.exit(1)
    
    # Step 3: Create directories
    create_directories()
    
    # Step 4: Initialize database
    if not await initialize_database():
        print("❌ Database initialization failed. Exiting.")
        sys.exit(1)
    
    # Step 5: Verify API keys
    check_api_keys()
    
    print("\n" + "=" * 60)
    print("✅ INITIALIZATION COMPLETE")
    print("=" * 60)
    print("🌐 API Documentation: http://localhost:8000/docs")
    print("📊 Health Check: http://localhost:8000/health")
    print("🔐 Default Login: admin / secret")
    print("=" * 60)
    
    # Step 6: Start server
    start_server()

def quick_start():
    """Quick start without full checks"""
    print("🚀 Quick starting Vaani Sentinel X...")
    
    # Create basic directories
    create_directories()
    
    # Start server
    start_server()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Vaani Sentinel X Startup")
    parser.add_argument("--quick", action="store_true", help="Quick start without full initialization")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    
    args = parser.parse_args()
    
    if args.quick:
        quick_start()
    else:
        asyncio.run(main())
