# Deployment Information

## Public URL
https://day12ha-tang-cloudvadeployment-production-f7db.up.railway.app/

## Platform
Railway

## Test Commands

### Health Check
```bash
vdp:day12_ha-tang-cloud_va_deployment (lab06) $ curl https://day12ha-tang-cloudvadeployment-production-f7db.up.railway.app/health
{"status":"ok","version":"1.0.0","environment":"development","uptime_seconds":3991.5,"total_requests":3,"checks":{"llm":"mock"},"timestamp":"2026-04-17T15:18:39.765130+00:00"}vdp:day12_ha-tang-cloud_va_deployment (lab06) $ 
```

### API Test (with authentication)
```bash
vdp:day12_ha-tang-cloud_va_deployment (lab06) $ curl -X POST https://day12ha-tang-cloudvadeployment-production-f7db.up.railway.app/ask \
  -H "X-API-Key: dev-key-change-me-in-production" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "question": "Hello"}'
{"question":"Hello","answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé.","model":"gpt-4o-mini","timestamp":"2026-04-17T15:23:48.317682+00:00"}vdp:day12_ha-tang-cloud_va_deployment (lab06) $ 
```

## Environment Variables Set
AGENT_API_KEY="dev-key-change-me-in-production"
ALLOWED_ORIGINS="http://localhost:3000"
APP_NAME="AI Agent"
APP_VERSION="1.0.0"
DAILY_BUDGET_USD="5.0"
DEBUG="true"
ENVIRONMENT="development"
HOST="0.0.0.0"
JWT_SECRET="ym)I4nKwek0M{x0(GH@;b>_&_L,^=vA{w*m"
LLM_MODEL="gpt-4o-mini"
PORT="8000"
PYTHONDONTWRITEBYTECODE="1"
PYTHONPATH="/app"
PYTHONUNBUFFERED="1"
RATE_LIMIT_PER_MINUTE="20"
REDIS_URL="redis://localhost:6379/0"

## Screenshots
- [Deployment dashboard](./assets/dashboard.png)
- [Service running](./assets/deployment.png)
- [Test results](./assets/testing.png)
- [CI](/./assets/ci_pipeline.png)
```
