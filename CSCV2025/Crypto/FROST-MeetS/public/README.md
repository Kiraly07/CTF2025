# TrustGuard Treasury

Enterprise-grade decentralized signature service using threshold cryptography.

---

## Quick Start

```bash
# Start the service
docker compose up -d

# Check health
curl http://localhost:8000/health

# Stop
docker compose down
```

The API runs at `http://localhost:8000`.

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/approvals/request` | POST | Request transaction approval |
| `/approvals/status/{id}` | GET | Check approval status |
| `/approvals/verify` | POST | Verify signature |
| `/health` | GET | Service health & public key |
| `/metrics` | GET | Operational metrics |

---

## Request Approval

```bash
curl -X POST http://localhost:8000/approvals/request \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "your_org_id",
    "message": "48656c6c6f"
  }'
```

Response includes:
- Session ID
- Aggregate signature (R, s)
- Council members who approved (5 of 9)
- Timestamp

---

## System Architecture

### Council-Based Approval
- **9 Council Members**: Distributed authority
- **5-Member Threshold**: Any 5 can approve
- **Intelligent Routing**: Prioritizes recently active members

### Performance
- **~200ms** average response time
- **Session Optimization**: Caching for improved throughput
- **Rate Limits**: 8 requests/minute per organization

---

## Configuration

Edit `docker-compose.yml` for local testing:

```yaml
environment:
  - SMART_ROUTING_PREFERENCE=60  # Member selection bias (0-100)
  - SESSION_OPTIMIZATION_TTL=90  # Cache duration (seconds)
  - RATE_LIMIT_PER_MINUTE=120    # Higher for local testing
  - MAX_CONCURRENT_SESSIONS=3
```

---

## Local Development

```bash
# Install dependencies
uv sync

# Run without Docker
uv run uvicorn src.main:app --reload
```

---

## Project Structure

```
src/
├── api/          # REST API endpoints
├── models/       # Data models
├── services/     # Business logic
│   ├── frost.py          # Threshold signatures
│   ├── nonce_cache.py    # Session optimization
│   ├── subset_selector.py # Intelligent routing
│   └── key_manager.py     # Key management
└── crypto/       # Cryptographic primitives
```

---

## Technical Details

- **Protocol**: FROST (Flexible Round-Optimized Schnorr Threshold)
- **Threshold**: 5-of-9 council members required
- **Curve**: secp256k1
- **Framework**: FastAPI + Python 3.11
- **Cryptography**: libsecp256k1 via coincurve

---

## Files Included

- `src/` - Complete source code
- `Dockerfile` - Container build
- `docker-compose.yml` - Local environment
- `pyproject.toml` - Dependencies
- `uv.lock` - Locked versions

---

**TrustGuard Treasury** - Enterprise threshold signatures made simple.
