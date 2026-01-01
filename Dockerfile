# Stage 1: Build stage with uv for dependency installation
FROM python:3.12-slim AS builder

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install CPU-only PyTorch first (much smaller than CUDA version)
RUN uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu --system

# Create virtual environment and install dependencies
RUN uv sync --frozen --no-dev

# Stage 2: Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies for psycopg2 and MinerU (OpenGL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Set PATH to use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY main.py ./
COPY backend ./backend

# Create output directories
RUN mkdir -p generated_files/pptx generated_files/pdf rag_storage rag_uploads rag_parsed

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
