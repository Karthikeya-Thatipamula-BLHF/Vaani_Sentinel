# Vaani Sentinel X Integration Guide
## How to Integrate with Other Projects

This guide shows how to integrate Vaani Sentinel X components into your existing projects.

## 🔌 Integration Methods

### 1. Direct Agent Import (Python Projects)

```python
# Import specific agents
from agents.translation_agent import get_translation_agent
from agents.sentiment_tuner import get_sentiment_tuner
from agents.adaptive_targeter import get_platform_targeter
from agents.analytics_collector import get_analytics_collector

# Initialize agents
translator = get_translation_agent()
sentiment = get_sentiment_tuner()
targeter = get_platform_targeter()
analytics = get_analytics_collector()

# Use in your application
def process_content(text, target_languages=["hi", "es"]):
    # Translate content
    translation_result = translator.translate_content(
        content_text=text,
        target_languages=target_languages,
        user_profile_id="general"
    )
    
    # Adjust sentiment
    sentiment_result = sentiment.adjust_sentiment(
        content_text=text,
        target_sentiment="uplifting",
        intensity="moderate"
    )
    
    # Target for platform
    platform_result = targeter.target_platform_content(
        content_text=sentiment_result["adjusted_content"],
        platform="instagram",
        context="motivational"
    )
    
    return {
        "translations": translation_result["translations"],
        "optimized_content": platform_result["final_content"],
        "hashtags": platform_result["hashtags"]
    }
```

### 2. REST API Integration (Any Language)

#### JavaScript/Node.js Example
```javascript
class VaaniClient {
    constructor(baseUrl = 'http://localhost:8000', credentials = {username: 'admin', password: 'secret'}) {
        this.baseUrl = baseUrl;
        this.credentials = credentials;
        this.token = null;
    }
    
    async authenticate() {
        const response = await fetch(`${this.baseUrl}/api/v1/auth/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(this.credentials)
        });
        
        if (response.ok) {
            const data = await response.json();
            this.token = data.access_token;
            return true;
        }
        return false;
    }
    
    async translateContent(text, languages) {
        if (!this.token) await this.authenticate();
        
        const response = await fetch(`${this.baseUrl}/api/v1/agents/translate-content`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content_text: text,
                target_languages: languages
            })
        });
        
        return response.json();
    }
    
    async adjustSentiment(text, sentiment = 'uplifting') {
        if (!this.token) await this.authenticate();
        
        const response = await fetch(`${this.baseUrl}/api/v1/agents/adjust-sentiment`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content_text: text,
                target_sentiment: sentiment,
                intensity: 'moderate'
            })
        });
        
        return response.json();
    }
    
    async targetPlatform(text, platform = 'instagram') {
        if (!this.token) await this.authenticate();
        
        const response = await fetch(`${this.baseUrl}/api/v1/agents/target-platform-content`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content_text: text,
                platform: platform
            })
        });
        
        return response.json();
    }
}

// Usage
const vaani = new VaaniClient();

async function processContent(text) {
    // Translate to multiple languages
    const translations = await vaani.translateContent(text, ['hi', 'es', 'fr']);
    
    // Adjust sentiment
    const sentiment = await vaani.adjustSentiment(text, 'motivational');
    
    // Optimize for Instagram
    const instagram = await vaani.targetPlatform(sentiment.adjusted_content, 'instagram');
    
    return {
        original: text,
        translations: translations.translations,
        optimized: instagram.final_content,
        hashtags: instagram.hashtags
    };
}
```

#### Python Requests Example
```python
import requests

class VaaniClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        
    def authenticate(self, username="admin", password="secret"):
        response = requests.post(f"{self.base_url}/api/v1/auth/login",
                               json={"username": username, "password": password})
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            return True
        return False
    
    def get_headers(self):
        return {"Authorization": f"Bearer {self.token}"}
    
    def translate_content(self, text, languages):
        if not self.token:
            self.authenticate()
            
        response = requests.post(f"{self.base_url}/api/v1/agents/translate-content",
                               json={"content_text": text, "target_languages": languages},
                               headers=self.get_headers())
        return response.json()
    
    def adjust_sentiment(self, text, sentiment="uplifting"):
        if not self.token:
            self.authenticate()
            
        response = requests.post(f"{self.base_url}/api/v1/agents/adjust-sentiment",
                               json={"content_text": text, "target_sentiment": sentiment},
                               headers=self.get_headers())
        return response.json()

# Usage
client = VaaniClient()
result = client.translate_content("Hello world", ["hi", "es"])
```

### 3. Microservice Integration

#### Docker Compose Example
```yaml
version: '3.8'
services:
  vaani-sentinel:
    build: ./vaani-sentinel-x
    ports:
      - "8000:8000"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    
  your-app:
    build: ./your-app
    depends_on:
      - vaani-sentinel
    environment:
      - VAANI_URL=http://vaani-sentinel:8000
```

## 🎯 Common Integration Patterns

### 1. Content Processing Pipeline
```python
def content_pipeline(raw_content):
    # Step 1: Clean and sanitize
    from agents.miner_sanitizer import get_miner_sanitizer
    miner = get_miner_sanitizer()
    cleaned = miner.sanitize_content(raw_content)
    
    # Step 2: Generate platform content
    from agents.ai_writer_voicegen import get_ai_writer
    writer = get_ai_writer()
    platform_content = writer.generate_platform_content(
        content_text=cleaned["sanitized_content"],
        platforms=["twitter", "instagram", "linkedin"]
    )
    
    # Step 3: Translate to multiple languages
    from agents.translation_agent import get_translation_agent
    translator = get_translation_agent()
    translations = translator.translate_content(
        content_text=cleaned["sanitized_content"],
        target_languages=["hi", "sa", "es"]
    )
    
    return {
        "original": raw_content,
        "cleaned": cleaned,
        "platform_content": platform_content,
        "translations": translations
    }
```

### 2. Analytics Integration
```python
def track_content_performance(content_id, platform, content_text):
    from agents.analytics_collector import get_analytics_collector
    analytics = get_analytics_collector()
    
    # Generate engagement stats
    stats = analytics.generate_task3_engagement_stats(
        content_id=content_id,
        platform=platform,
        content_text=content_text
    )
    
    # Get feedback signals
    feedback = analytics.create_feedback_signals(days_back=7)
    
    return {
        "engagement": stats,
        "feedback": feedback
    }
```

### 3. Real-time Content Optimization
```python
def optimize_content_realtime(content, target_platform, user_profile):
    # Sentiment adjustment
    from agents.sentiment_tuner import get_sentiment_tuner
    sentiment = get_sentiment_tuner()
    
    # Platform targeting
    from agents.adaptive_targeter import get_platform_targeter
    targeter = get_platform_targeter()
    
    # Optimize sentiment
    optimized = sentiment.adjust_sentiment(
        content_text=content,
        target_sentiment="motivational",
        intensity="moderate"
    )
    
    # Target platform
    targeted = targeter.target_platform_content(
        content_text=optimized["adjusted_content"],
        platform=target_platform,
        context="motivational"
    )
    
    return targeted["final_content"]
```

## 🔧 Configuration for Integration

### 1. Custom Configuration
```python
# config/integration_config.py
INTEGRATION_CONFIG = {
    "api_base_url": "http://localhost:8000",
    "default_languages": ["en", "hi", "es"],
    "default_platforms": ["instagram", "twitter"],
    "sentiment_preferences": {
        "marketing": "uplifting",
        "education": "professional",
        "entertainment": "energetic"
    },
    "voice_preferences": {
        "formal": "professional",
        "casual": "conversational",
        "spiritual": "devotional"
    }
}
```

### 2. Environment Variables
```bash
# .env file for your project
VAANI_API_URL=http://localhost:8000
VAANI_USERNAME=admin
VAANI_PASSWORD=secret
VAANI_DEFAULT_LANGUAGES=hi,es,fr
VAANI_DEFAULT_PLATFORMS=instagram,twitter
```

## 🚀 Production Integration

### 1. Load Balancing
```nginx
# nginx.conf
upstream vaani_backend {
    server vaani-1:8000;
    server vaani-2:8000;
    server vaani-3:8000;
}

server {
    listen 80;
    location /vaani/ {
        proxy_pass http://vaani_backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. Health Monitoring
```python
def check_vaani_health():
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def fallback_processing(content):
    # Fallback logic when Vaani is unavailable
    return {"content": content, "status": "fallback"}
```

## 📚 Integration Examples

### 1. Blog Platform Integration
```python
class BlogPlatform:
    def __init__(self):
        self.vaani = VaaniClient()
    
    def publish_post(self, title, content, target_languages=None):
        # Optimize content
        optimized = self.vaani.adjust_sentiment(content, "inspirational")
        
        # Generate social media previews
        social_previews = {}
        for platform in ["twitter", "instagram", "linkedin"]:
            preview = self.vaani.target_platform(optimized["adjusted_content"], platform)
            social_previews[platform] = preview
        
        # Translate if needed
        translations = {}
        if target_languages:
            translations = self.vaani.translate_content(content, target_languages)
        
        return {
            "title": title,
            "content": optimized["adjusted_content"],
            "social_previews": social_previews,
            "translations": translations
        }
```

### 2. E-commerce Product Descriptions
```python
class ProductDescriptionGenerator:
    def __init__(self):
        from agents.ai_writer_voicegen import get_ai_writer
        from agents.translation_agent import get_translation_agent
        
        self.writer = get_ai_writer()
        self.translator = get_translation_agent()
    
    def generate_descriptions(self, product_data, target_markets):
        # Generate base description
        base_content = self.writer.generate_platform_content(
            content_text=product_data["features"],
            platforms=["ecommerce"],
            tone="persuasive"
        )
        
        # Translate for different markets
        descriptions = {}
        for market in target_markets:
            language = market["language"]
            translated = self.translator.translate_content(
                content_text=base_content["platform_content"]["ecommerce"],
                target_languages=[language],
                user_profile_id=market["profile"]
            )
            descriptions[market["name"]] = translated["translations"][language]
        
        return descriptions
```

## 🔒 Security Considerations

### 1. API Key Management
```python
# Use environment variables
import os
VAANI_API_KEY = os.getenv('VAANI_API_KEY')
VAANI_SECRET = os.getenv('VAANI_SECRET')

# Implement token refresh
def refresh_token_if_needed(client):
    if client.token_expired():
        client.authenticate()
```

### 2. Rate Limiting
```python
import time
from functools import wraps

def rate_limit(calls_per_minute=60):
    def decorator(func):
        last_called = [0.0]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = 60.0 / calls_per_minute - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

@rate_limit(calls_per_minute=30)
def call_vaani_api(endpoint, data):
    # Your API call here
    pass
```

## 📊 Monitoring Integration

### 1. Metrics Collection
```python
import logging
import time

class VaaniMetrics:
    def __init__(self):
        self.call_count = 0
        self.total_time = 0
        self.errors = 0
    
    def track_call(self, func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                self.call_count += 1
                self.total_time += time.time() - start_time
                return result
            except Exception as e:
                self.errors += 1
                logging.error(f"Vaani API error: {e}")
                raise
        return wrapper
    
    def get_stats(self):
        return {
            "calls": self.call_count,
            "avg_time": self.total_time / max(self.call_count, 1),
            "error_rate": self.errors / max(self.call_count, 1)
        }
```

---

This integration guide provides comprehensive examples for integrating Vaani Sentinel X into your projects. Choose the method that best fits your architecture and requirements!
