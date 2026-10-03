# ==================================================================
# TrustGuard Treasury - Production Deployment Dockerfile
# ==================================================================
# Multi-stage build for optimized production image
# Final image size: <200MB
# Python 3.11 + FastAPI + coincurve (secp256k1)

# ==================================================================
# Stage 1: Dependency Builder
# ==================================================================
FROM python:3.11-slim as builder

# Install uv package manager for fast, reproducible dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set application working directory
WORKDIR /app

# Copy dependency manifests and project metadata
# README.md required by pyproject.toml metadata
COPY pyproject.toml uv.lock README.md ./

# Install production dependencies into isolated virtual environment
# --frozen: Use exact versions from uv.lock (reproducible builds)
# --no-dev: Exclude development dependencies (testing, linting)
RUN uv sync --frozen --no-dev

# ==================================================================
# Stage 2: Production Runtime
# ==================================================================
FROM python:3.11-slim

# Set application working directory
WORKDIR /app

# Copy pre-built virtual environment from builder stage
# Avoids compilation in runtime image
COPY --from=builder /app/.venv /app/.venv

# Copy application source code
COPY src/ ./src/
COPY pyproject.toml ./

# Production environment configuration
# Add venv to PATH for dependency access
ENV PATH="/app/.venv/bin:$PATH"
# Real-time log output (no buffering)
ENV PYTHONUNBUFFERED=1
# Default optimization cache size
ENV NONCE_CACHE_SIZE=10000

# Expose service port
EXPOSE 8000

# Container health monitoring
# Polls /health endpoint every 30s to verify service availability
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Start TrustGuard Treasury service
# FastAPI with Uvicorn ASGI server on all interfaces
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

