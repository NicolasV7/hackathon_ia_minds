FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --production=false --legacy-peer-deps
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
COPY --from=builder /app/dist ./dist
RUN npm i -g serve@14.1.2 --silent
EXPOSE 3000
CMD ["serve", "-s", "dist", "-l", "3000"]
