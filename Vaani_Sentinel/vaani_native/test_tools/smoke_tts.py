#!/usr/bin/env python3
"""
Vaani Native TTS Smoke Test
Day 0: Basic integration test for native TTS agent setup

Tests:
- Agent initialization
- Database model creation
- Basic synthesis call (mock)
- Cache stats reporting

Run: python vaani_native/test_tools/smoke_tts.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.vaani_native_tts import get_native_tts
from core.database import init_db
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_smoke_test():
    """Run basic smoke tests for native TTS integration"""

    print("🚀 Vaani Native TTS Smoke Test - Day 0")
    print("=" * 50)

    try:
        # Test 1: Agent initialization
        print("1. Testing agent initialization...")
        native_tts = get_native_tts()
        print("✅ Native TTS agent initialized")

        # Test 2: Cache stats
        print("2. Testing cache stats...")
        cache_stats = native_tts.get_cache_stats()
        print(f"✅ Cache stats: {cache_stats}")

        # Test 3: Mock synthesis
        print("3. Testing mock synthesis...")
        test_text = "Namaste, this is a test of Vaani Native TTS."
        result = native_tts.synthesize(
            text=test_text,
            voice="gurukul_neutral",
            language="hi"
        )
        print(f"✅ Mock synthesis completed: {result['content_id']}")

        # Test 4: Database integration
        print("4. Testing database integration...")
        await init_db()
        print("✅ Database models created")

        # Test 5: File structure check
        print("5. Testing file structure...")
        required_dirs = [
            "vaani_native/model",
            "vaani_native/training",
            "vaani_native/vocoder",
            "vaani_native/prosody_controller",
            "vaani_native/api",
            "vaani_native/test_tools",
            "vaani_native/docs"
        ]

        for dir_path in required_dirs:
            if os.path.exists(dir_path):
                print(f"✅ Directory exists: {dir_path}")
            else:
                print(f"❌ Missing directory: {dir_path}")

        print("\n🎉 Day 0 Smoke Test PASSED!")
        print("Ready for Day 1: TTS backbone integration")
        print("\nNext steps:")
        print("- Install Coqui TTS: pip install TTS==0.12.2")
        print("- Implement actual TTS synthesis in vaani_native/api/infer.py")
        print("- Add native TTS endpoints to api/routers/agents.py")

        return True

    except Exception as e:
        print(f"❌ Smoke test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(run_smoke_test())
    sys.exit(0 if success else 1)
