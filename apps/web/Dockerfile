# ==============================================================================
# Production Dockerfile for Agentic Multimodal Research Platform Web (Frontend)
# Multi-stage Vite + TypeScript build and lightweight Nginx alpine server
# ==============================================================================

FROM node:20-alpine AS builder

WORKDIR /app

# Copy package descriptors
COPY package*.json ./
RUN npm ci

# Copy source assets
COPY . .

# Build production bundle
RUN npm run build

# ==============================================================================
# Production Nginx Runtime Stage
# ==============================================================================
FROM nginx:alpine AS runner

# Remove default nginx html
RUN rm -rf /usr/share/nginx/html/*

# Copy built frontend assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
