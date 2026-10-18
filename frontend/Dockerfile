# Сборка фронтенда
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# API на том же домене по пути /api (проксирует Caddy), поэтому CORS в production не нужен
ENV VITE_API_URL=/api
RUN npm run build

# Раздача статики + HTTPS + проксирование API
FROM caddy:2-alpine
COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=build /app/dist /srv
