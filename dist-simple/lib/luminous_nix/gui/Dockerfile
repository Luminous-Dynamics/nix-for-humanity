# Multi-stage Dockerfile for AI-Driven Interface Generation System

# Stage 1: Builder
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 luminous && \
    mkdir -p /data /config /logs /app && \
    chown -R luminous:luminous /data /config /logs /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/luminous/.local

# Set working directory
WORKDIR /app

# Copy application files
COPY --chown=luminous:luminous *.py ./
COPY --chown=luminous:luminous deploy.sh health_check.sh ./

# Make scripts executable
RUN chmod +x deploy.sh health_check.sh

# Switch to non-root user
USER luminous

# Add local bin to PATH
ENV PATH=/home/luminous/.local/bin:$PATH

# Set Python path
ENV PYTHONPATH=/app:$PYTHONPATH

# Environment variables
ENV LUMINOUS_DATA_DIR=/data \
    LUMINOUS_CONFIG_DIR=/config \
    LUMINOUS_LOG_DIR=/logs \
    FLASK_APP=api_server.py

# Create necessary directories
RUN mkdir -p /data/cache /data/deployment

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Expose port
EXPOSE 5000

# Default command - run API server
CMD ["python", "api_server.py", "--host", "0.0.0.0", "--port", "5000"]