# ─────────────────────────────────────────────────────────────────────────────
# DriveSafe AI — Hugging Face Spaces Dockerfile
# Full-stack: React frontend (built) + Flask backend + AI models (TF, YOLO, MP)
# Port: 7860 (required by Hugging Face Spaces)
# ─────────────────────────────────────────────────────────────────────────────

# Stage 1: Build the React/Vite frontend
FROM node:20-slim AS frontend-builder

WORKDIR /build/frontend

# Copy package files first for better layer caching
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --prefer-offline

# Copy full frontend source
COPY frontend/ ./

# Build production bundle (outputs to /build/frontend/dist)
RUN npm run build


# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: Python backend + serve built frontend
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.10-slim

# System libraries required by OpenCV, MediaPipe, and report generation fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    libfreetype6 \
    libfontconfig1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security (Hugging Face requirement)
RUN useradd -m -u 1000 appuser

WORKDIR /app

# ── Python dependencies ───────────────────────────────────────────────────────
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# ── Backend application code ──────────────────────────────────────────────────
COPY backend/ ./

# ── Built React frontend (from Stage 1) ──────────────────────────────────────
COPY --from=frontend-builder /build/frontend/dist ./static_frontend

# ── Ensure runtime directories exist and are writable ────────────────────────
RUN mkdir -p screenshots reports && chown -R appuser:appuser /app

USER appuser

# ── Environment defaults (overridden by HF Space Secrets) ────────────────────
ENV PORT=7860 \
    FLASK_ENV=production \
    FLASK_DEBUG=False \
    CORS_ORIGINS=* \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 7860

# ── Start Flask with Gunicorn ─────────────────────────────────────────────────
# 1 worker keeps memory under control for the free HF CPU tier (16 GB RAM)
# timeout=180 because TF model loading can take ~30s on cold start
CMD ["gunicorn", "app:app", \
     "--bind", "0.0.0.0:7860", \
     "--workers", "1", \
     "--threads", "4", \
     "--timeout", "180", \
     "--worker-class", "gthread", \
     "--log-level", "info", \
     "--access-logfile", "-"]
