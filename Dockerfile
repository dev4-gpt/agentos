# AgentOS Registry - Production Dockerfile
FROM python:3.11-slim AS base

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
RUN pip install uv

# Copy dependency files
COPY pyproject.toml ./
COPY README.md ./
COPY src/ ./src/

# Install production dependencies
RUN uv pip install --system --no-cache .


# Create non-root user
RUN useradd -m -u 1000 agentos && chown -R agentos:agentos /app
USER agentos

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "agentos.registry.server:app", "--host", "0.0.0.0", "--port", "8000"]
