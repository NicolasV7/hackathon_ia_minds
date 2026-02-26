# ============================================================================
#  UPTC EcoEnergy Frontend - Dockerfile
#  Multi-stage build: deps -> build -> nginx production
# ============================================================================

# ------ Stage 1: Install Node dependencies ------
FROM node:20-alpine AS deps
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci --legacy-peer-deps && npm cache clean --force

# ------ Stage 2: Build the React app ------
FROM node:20-alpine AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# VITE_API_URL is a build-time variable baked into the JS bundle.
# When using Docker Compose, leave it empty — nginx proxies /api/ to backend.
ARG VITE_API_URL=
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# ------ Stage 3: Serve with nginx ------
FROM nginx:alpine AS production

# Replace default nginx config with our custom SPA + API proxy config
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built static files
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80 || exit 1

CMD ["nginx", "-g", "daemon off;"]
