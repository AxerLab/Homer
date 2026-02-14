# Stage 1: Build stage with uv for dependency installation
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Create virtual environment and install dependencies
RUN uv sync --no-dev

# Stage 2: Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Set PATH to use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY server.py ./

# Expose port
EXPOSE 8003

# Run the service
CMD ["python", "server.py"]
