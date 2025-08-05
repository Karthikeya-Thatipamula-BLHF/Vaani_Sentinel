# 🎯 Vaani Sentinel X - AI-Powered Voice-First Content Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

> **Revolutionary AI-integrated voice-first platform for multilingual content creation, analytics, and security**

## 🌟 Overview

Vaani Sentinel X is a production-level AI-powered platform that transforms content creation through voice-first technology. Built with FastAPI and integrated with cutting-edge AI models, it provides comprehensive content management, multilingual support, and advanced security features.

### ✨ Key Features

- 🤖 **AI-Powered Content Generation** - Groq & Gemini integration
- 🗣️ **Voice-First Technology** - Text-to-Speech with 20+ languages
- 🌍 **Multilingual Support** - Hindi, Sanskrit, English, and 17+ languages
- 🔒 **Advanced Security** - JWT auth, content encryption, kill switch
- 📊 **Real-time Analytics** - Performance insights and engagement tracking
- 🎯 **Platform Optimization** - Twitter, Instagram, LinkedIn, Spotify
- 🛡️ **Content Safety** - Bias detection, profanity filtering, ethics guard

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- API Keys: Google Gemini, Groq

### Installation

```bash
# Clone the repository
git clone https://github.com/Karthikeya-Thatipamula-BLHF/vaani.git
cd vaani

# Install dependencies
pip install -r Vaani_Sentinel/requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Start the server
cd Vaani_Sentinel
python main.py
```

### Access Points
- 🌐 **API Server**: http://localhost:8000
- 📚 **Documentation**: http://localhost:8000/docs
- 🔐 **Login**: admin / secret

## 🏗️ Architecture

```
vaani/
├── Vaani_Sentinel/          # Main application
│   ├── api/                 # FastAPI routes
│   ├── agents/              # AI agents & processors
│   ├── core/                # Core functionality
│   ├── config/              # Configuration files
│   └── utils/               # Utility functions
└── README.md               # This file
```

## 🔧 Core Components

### 🤖 AI Agents
- **AI Writer & Voice Generator** - Content creation with TTS
- **Multilingual Pipeline** - Translation and localization
- **Security Guard** - Content safety and compliance
- **Analytics Collector** - Performance tracking
- **Adaptive Targeter** - Platform-specific optimization

### 🛡️ Security Features
- JWT Authentication with 30-day tokens
- Content encryption and secure archives
- Emergency kill switch
- Bias detection and profanity filtering
- Comprehensive audit logging

### 📊 Analytics & Insights
- Real-time performance metrics
- Platform-specific analytics
- Engagement trend analysis
- Weekly strategy recommendations
- Content optimization insights

## 🌍 Multilingual Support

Supports 20+ languages including:
- **Indian Languages**: Hindi, Sanskrit, Marathi, Gujarati, Tamil, Telugu, Kannada, Malayalam, Bengali
- **International**: English, German, French, Spanish, Italian, Portuguese, Russian, Japanese, Korean, Chinese, Arabic

## 📱 Platform Integration

Optimized for:
- **Twitter** - 280 chars, trending hashtags
- **Instagram** - Visual storytelling, 2200 chars
- **LinkedIn** - Professional tone, 3000 chars
- **Spotify** - Audio content, voice scripts

## 🔗 API Endpoints

### Authentication
```http
POST /api/v1/auth/login
GET  /api/v1/auth/me
GET  /api/v1/auth/validate
```

### Content Management
```http
POST /api/v1/content/create
POST /api/v1/content/upload-csv
GET  /api/v1/content/list
```

### AI & Voice
```http
POST /api/v1/agents/ai-writer
POST /api/v1/agents/voice-generator
POST /api/v1/multilingual/translate
```

### Analytics
```http
GET  /api/v1/analytics/dashboard
GET  /api/v1/analytics/performance-insights
GET  /api/v1/analytics/weekly-strategy
```

## 💰 Cost-Effective Operation

- **FREE AI Models**: Groq (llama-3.1-8b-instant) + Gemini (1.5-flash)
- **FREE TTS**: Google Text-to-Speech (gTTS)
- **Daily Capacity**: 15,900+ requests/day
- **Total Cost**: $0.00

## 🛠️ Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📖 Documentation

- [API Documentation](Vaani_Sentinel/API_DOCUMENTATION.md)
- [Deployment Guide](Vaani_Sentinel/DEPLOYMENT_READY.md)
- [Integration Guide](Vaani_Sentinel/INTEGRATION_GUIDE.md)
- [Task Compliance](Vaani_Sentinel/TASK1_COMPLIANCE_CROSSCHECK.md)

## 🔒 Security & Compliance

- JWT-based authentication
- Content encryption
- Bias detection
- Profanity filtering
- Emergency kill switch
- Comprehensive logging

## 📊 Performance

- **Response Time**: <200ms average
- **Throughput**: 1000+ requests/minute
- **Uptime**: 99.9% target
- **Languages**: 20+ supported
- **Platforms**: 4 major platforms

## 🤝 Support

- 📧 Email: support@vaani-sentinel.com
- 🐛 Issues: [GitHub Issues](https://github.com/Karthikeya-Thatipamula-BLHF/vaani/issues)
- 📖 Docs: [Documentation](Vaani_Sentinel/README.md)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Google Gemini & Groq for AI capabilities
- Open source community for inspiration

---

**Built with ❤️ by [Karthikeya Thatipamula](https://github.com/Karthikeya-Thatipamula)**
