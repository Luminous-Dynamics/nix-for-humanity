# Multi-stage Dockerfile for NixOS GUI

# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend

# Copy frontend dependencies
COPY frontend/package*.json ./
RUN npm ci --only=production

# Copy frontend source
COPY frontend/ ./

# Build frontend
RUN npm run build

# Stage 2: Build backend
FROM node:18-alpine AS backend-builder
WORKDIR /app

# Install build dependencies
RUN apk add --no-cache python3 make g++

# Copy backend dependencies
COPY package*.json ./
COPY backend/package*.json ./backend/
RUN npm ci --only=production
RUN cd backend && npm ci --only=production

# Copy backend source
COPY backend/ ./backend/

# Stage 3: Runtime
FROM node:18-alpine
WORKDIR /app

# Install runtime dependencies
RUN apk add --no-cache \
    dbus \
    sudo \
    shadow \
    && rm -rf /var/cache/apk/*

# Create non-root user
RUN groupadd -r nixos-gui && \
    useradd -r -g nixos-gui -G wheel -m -s /bin/sh nixos-gui

# Copy built application
COPY --from=backend-builder /app/node_modules ./node_modules
COPY --from=backend-builder /app/backend ./backend
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Copy configuration files
COPY package.json ./
COPY .env.example ./.env

# Create necessary directories
RUN mkdir -p /var/lib/nixos-gui /var/log/nixos-gui && \
    chown -R nixos-gui:nixos-gui /var/lib/nixos-gui /var/log/nixos-gui /app

# Security: Drop capabilities
RUN setcap -r /usr/bin/node || true

# Environment variables
ENV NODE_ENV=production \
    PORT=8080 \
    HOST=0.0.0.0 \
    LOG_LEVEL=info

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD node -e "require('http').get('http://localhost:8080/api/health', (res) => process.exit(res.statusCode === 200 ? 0 : 1))"

# Switch to non-root user
USER nixos-gui

# Expose port
EXPOSE 8080

# Start application
CMD ["node", "backend/src/server.js"]