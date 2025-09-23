#!/bin/bash
# Vaani Native TTS Production Runner
# Day 4: Production deployment script

set -e  # Exit on any error

echo "🚀 Starting Vaani Native TTS Production Server"
echo "=============================================="

# Environment setup
export PYTHONPATH="$(pwd)"
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
export TTS_HOME="${TTS_HOME:-./tts_cache}"

# GPU check
if command -v nvidia-smi &> /dev/null; then
    echo "🎮 GPU Status:"
    nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader,nounits
    echo ""
fi

# Create necessary directories
echo "📁 Creating production directories..."
mkdir -p \
    vaani_native/model \
    vaani_native/training \
    vaani_native/vocoder \
    vaani_native/prosody_controller \
    vaani_native/api \
    vaani_native/test_tools \
    cache/native_tts \
    output/native_tts \
    data/vaani_voice \
    logs \
    tts_cache

# Pre-download TTS models (optional - speeds up first request)
echo "⬇️  Pre-downloading TTS models..."
python3 -c "
from TTS.api import TTS
print('Downloading TTS models...')
try:
    TTS('tts_models/en/ljspeech/tacotron2-DDC_ph')
    print('✅ TTS model ready')
except Exception as e:
    print(f'⚠️  Model download failed (will download on first use): {e}')

try:
    TTS('vocoder_models/en/ljspeech/hifigan_v2')
    print('✅ Vocoder model ready')
except Exception as e:
    print(f'⚠️  Vocoder download failed (will download on first use): {e}')
" || echo "Model pre-download skipped"

# Database migration
echo "🗄️  Running database migrations..."
python3 -c "
from core.database import init_db
import asyncio
asyncio.run(init_db())
print('✅ Database ready')
"

# Model loading test
echo "🧪 Testing model loading..."
python3 -c "
try:
    from vaani_native.api.infer import get_tts_inference
    inference = get_tts_inference()
    info = inference.get_model_info()
    print('✅ Models loaded successfully')
    print(f'   Device: {info[\"device\"]}')
    print(f'   Sample Rate: {info[\"sample_rate\"]}')
except Exception as e:
    echo \"❌ Model loading failed: $e\"
    exit 1
"

# Start server
echo "🌐 Starting production server..."
echo "📊 Monitoring available at: http://localhost:8000"
echo "📖 API docs available at: http://localhost:8000/docs"
echo "🛑 Press Ctrl+C to stop"
echo ""

# Start with production settings
exec python3 start_server.py \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 1 \
    --log-level info \
    --access-log \
    2>&1 | tee logs/native_tts_$(date +%Y%m%d_%H%M%S).log
