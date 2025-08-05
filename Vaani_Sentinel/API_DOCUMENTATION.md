# Vaani Sentinel X - API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
All API endpoints (except `/health` and `/docs`) require authentication using JWT tokens.

### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "secret"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 2592000,
  "user_id": "admin"
}
```

### Use Token
Include the token in the Authorization header:
```http
Authorization: Bearer <access_token>
```

## Content Management

### Create Content
```http
POST /api/v1/content/create
Authorization: Bearer <token>
Content-Type: application/json

{
  "text": "Your content here",
  "content_type": "tweet",
  "language": "en",
  "metadata": {}
}
```

### Upload CSV Content
```http
POST /api/v1/content/upload-csv
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: content.csv
```

### Upload JSON Content
```http
POST /api/v1/content/upload-json
Authorization: Bearer <token>
Content-Type: application/json

{
  "file_type": "json",
  "data": [
    {"text": "Content 1"},
    {"text": "Content 2"}
  ]
}
```

### List Content
```http
GET /api/v1/content/list?skip=0&limit=100&verified_only=false
Authorization: Bearer <token>
```

### Get Specific Content
```http
GET /api/v1/content/{content_id}
Authorization: Bearer <token>
```

## AI Content Generation

### Generate Platform Content
```http
POST /api/v1/agents/generate-content
Authorization: Bearer <token>
Content-Type: application/json

{
  "content_id": "content-uuid",
  "platforms": ["twitter", "instagram", "linkedin"],
  "tone": "casual",
  "language": "en"
}
```

**Response:**
```json
{
  "content_id": "content-uuid",
  "generated_content": {
    "twitter": "Generated tweet content...",
    "instagram": "Generated Instagram post...",
    "linkedin": "Generated LinkedIn post..."
  },
  "voice_scripts": {
    "en": "Voice script content..."
  },
  "metadata": {
    "tone": "casual",
    "language": "en",
    "platforms": ["twitter", "instagram", "linkedin"],
    "created_at": "2024-01-01T00:00:00Z"
  },
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Generate Voice Content
```http
POST /api/v1/agents/generate-voice
Authorization: Bearer <token>
Content-Type: application/json

{
  "content_id": "content-uuid",
  "language": "hi",
  "tone": "devotional",
  "voice_tag": "hi_in_female_devotional"
}
```

### Batch Generate Content
```http
POST /api/v1/agents/batch-generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "content_ids": ["id1", "id2", "id3"],
  "platforms": ["twitter", "instagram"],
  "tone": "uplifting",
  "language": "en"
}
```

### Get Supported Platforms
```http
GET /api/v1/agents/platforms
Authorization: Bearer <token>
```

### Get Supported Tones
```http
GET /api/v1/agents/tones
Authorization: Bearer <token>
```

### Get Supported Languages
```http
GET /api/v1/agents/languages
Authorization: Bearer <token>
```

## Multilingual Processing

### Detect Language
```http
POST /api/v1/multilingual/detect-language
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "Text to analyze for language detection"
}
```

### Process Multilingual Content
```http
POST /api/v1/multilingual/process-multilingual
Authorization: Bearer <token>
Content-Type: application/json

{
  "content_id": "content-uuid",
  "target_languages": ["hi", "sa", "mr"],
  "auto_detect": true
}
```

### Translate Content
```http
POST /api/v1/multilingual/translate
Authorization: Bearer <token>
Content-Type: application/json

{
  "content_id": "content-uuid",
  "target_languages": ["hi", "sa"],
  "tone": "neutral"
}
```

### Batch Translate
```http
POST /api/v1/multilingual/batch-translate
Authorization: Bearer <token>
Content-Type: application/json

{
  "content_ids": ["id1", "id2"],
  "target_languages": ["hi", "sa", "mr"]
}
```

### Get Content Translations
```http
GET /api/v1/multilingual/translations/{content_id}
Authorization: Bearer <token>
```

## Analytics

### Generate Engagement Metrics
```http
POST /api/v1/analytics/generate-engagement
Authorization: Bearer <token>
Content-Type: application/json

{
  "post_id": "post-uuid",
  "platform": "twitter",
  "content_type": "inspirational",
  "language": "en",
  "posting_time": "2024-01-01T12:00:00Z"
}
```

**Response:**
```json
{
  "analytics_id": "analytics-uuid",
  "post_id": "post-uuid",
  "platform": "twitter",
  "views": 1250,
  "likes": 45,
  "shares": 8,
  "comments": 12,
  "clicks": 23,
  "saves": 6,
  "engagement_rate": 0.0752,
  "reach": 1100,
  "impressions": 1250,
  "created_at": "2024-01-01T12:00:00Z"
}
```

### Get Performance Insights
```http
GET /api/v1/analytics/performance-insights?days=7
Authorization: Bearer <token>
```

### Get Weekly Strategy
```http
GET /api/v1/analytics/weekly-strategy
Authorization: Bearer <token>
```

### Get Post Analytics
```http
GET /api/v1/analytics/post-analytics/{post_id}
Authorization: Bearer <token>
```

### Platform Comparison
```http
GET /api/v1/analytics/platform-comparison?days=30
Authorization: Bearer <token>
```

### Engagement Trends
```http
GET /api/v1/analytics/engagement-trends?days=30&platform=twitter
Authorization: Bearer <token>
```

## Security

### Analyze Content Security
```http
POST /api/v1/security/analyze-content
Authorization: Bearer <token>
Content-Type: application/json

{
  "content_id": "content-uuid"
}
```

**Response:**
```json
{
  "content_id": "content-uuid",
  "flags_count": 2,
  "flags": [
    {
      "flag_id": "flag-uuid",
      "type": "profanity",
      "severity": "medium",
      "details": {
        "matches": ["word1", "word2"],
        "count": 2
      },
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "risk_level": "medium",
  "recommendations": [
    "Remove profane language before publishing",
    "Consider neutral rephrasing"
  ]
}
```

### Encrypt Content
```http
POST /api/v1/security/encrypt-content
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "Content to encrypt",
  "language": "en"
}
```

### Create Encrypted Archive
```http
POST /api/v1/security/create-archive
Authorization: Bearer <token>
Content-Type: application/json

{
  "content_ids": ["id1", "id2"],
  "language": "en"
}
```

### Kill Switch Operations
```http
# Activate kill switch
POST /api/v1/security/kill-switch/activate
Authorization: Bearer <token>
Content-Type: application/json

{
  "reason": "Security breach detected"
}

# Deactivate kill switch
POST /api/v1/security/kill-switch/deactivate
Authorization: Bearer <token>

# Check kill switch status
GET /api/v1/security/kill-switch/status
Authorization: Bearer <token>
```

### Security Dashboard
```http
GET /api/v1/security/dashboard
Authorization: Bearer <token>
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid input)
- `401`: Unauthorized (invalid/missing token)
- `404`: Not Found (resource doesn't exist)
- `500`: Internal Server Error

## Rate Limiting

API endpoints are rate-limited to prevent abuse:
- Authentication endpoints: 5 requests per minute
- Content creation: 100 requests per hour
- AI generation: 50 requests per hour
- Analytics: 200 requests per hour

## Data Models

### Content Types
- `tweet`: Twitter post (≤280 characters)
- `instagram_post`: Instagram post (≤2200 characters)
- `linkedin_post`: LinkedIn post (≤3000 characters)
- `voice_script`: Voice script (20-30 seconds)

### Platforms
- `twitter`: Twitter social media platform
- `instagram`: Instagram social media platform
- `linkedin`: LinkedIn professional platform
- `spotify`: Spotify audio platform

### Tones
- `formal`: Professional, business-appropriate
- `casual`: Friendly, conversational
- `devotional`: Spiritual, calming
- `neutral`: Balanced, informative
- `uplifting`: Positive, motivational

### Languages
Supported languages include:
- **Indian**: `hi` (Hindi), `sa` (Sanskrit), `mr` (Marathi), `gu` (Gujarati), `ta` (Tamil), `te` (Telugu), `kn` (Kannada), `ml` (Malayalam), `bn` (Bengali)
- **Global**: `en` (English), `de` (German), `fr` (French), `es` (Spanish), `it` (Italian), `pt` (Portuguese), `ru` (Russian), `ja` (Japanese), `ko` (Korean), `zh` (Chinese), `ar` (Arabic)

## WebSocket Support

Real-time updates are available through WebSocket connections:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    // Handle real-time updates
};
```

## SDK Examples

### Python SDK Usage
```python
import requests

class VaaniClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.token = self._login(username, password)
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def _login(self, username, password):
        response = requests.post(f"{self.base_url}/api/v1/auth/login",
                               json={"username": username, "password": password})
        return response.json()["access_token"]
    
    def create_content(self, text, content_type="tweet", language="en"):
        return requests.post(f"{self.base_url}/api/v1/content/create",
                           json={"text": text, "content_type": content_type, "language": language},
                           headers=self.headers).json()
    
    def generate_content(self, content_id, platforms=None, tone="neutral"):
        return requests.post(f"{self.base_url}/api/v1/agents/generate-content",
                           json={"content_id": content_id, "platforms": platforms, "tone": tone},
                           headers=self.headers).json()

# Usage
client = VaaniClient("http://localhost:8000", "admin", "secret")
content = client.create_content("Hello world!")
generated = client.generate_content(content["content_id"], ["twitter", "instagram"])
```
