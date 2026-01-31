# UPTC EcoEnergy Frontend - Vite + React Production Dockerfile
# Multi-stage build for optimized deployment

# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies with legacy peer deps to handle react-leaflet conflict
RUN npm ci --legacy-peer-deps && npm cache clean --force

# Stage 2: Builder
FROM node:20-alpine AS builder
WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build argument for API URL
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

# Build the application
RUN npm run build

# Stage 3: Production with nginx
FROM nginx:alpine AS production

# Copy custom nginx config
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80 || exit 1

# Run nginx
CMD ["nginx", "-g", "daemon off;"]
