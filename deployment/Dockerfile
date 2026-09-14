# Build with the shared parent directory as context; see docker-compose.yml.
FROM node:20-bookworm-slim AS frontend-build

WORKDIR /build/frontend
COPY SamadiFarm-FrontEnd/package.json SamadiFarm-FrontEnd/package-lock.json ./
RUN npm ci
COPY SamadiFarm-FrontEnd/ ./
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
RUN npm run build && npm prune --omit=dev

FROM python:3.12-slim-bookworm AS backend-build

WORKDIR /build/backend
COPY samadi-farm-backend/requirements.txt ./
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM caddy:2.10-alpine AS caddy-runtime

FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_DATABASE_PATH=/data/db.sqlite3 \
    DJANGO_MEDIA_ROOT=/data/media

WORKDIR /app
RUN apt-get update \
    && apt-get install -y --no-install-recommends supervisor \
    && rm -rf /var/lib/apt/lists/*
COPY --from=frontend-build /usr/local/bin/node /usr/local/bin/node
COPY --from=caddy-runtime /usr/bin/caddy /usr/local/bin/caddy
COPY --from=backend-build /wheels /wheels
COPY samadi-farm-backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r /tmp/requirements.txt \
    && rm -rf /wheels /tmp/requirements.txt
COPY samadi-farm-backend/ /app/backend/
COPY --from=frontend-build /build/frontend/.next /app/frontend/.next
COPY --from=frontend-build /build/frontend/public /app/frontend/public
COPY --from=frontend-build /build/frontend/package.json /app/frontend/package.json
COPY --from=frontend-build /build/frontend/node_modules /app/frontend/node_modules
COPY samadi-farm-backend/deployment/supervisord.conf /etc/supervisor/conf.d/samadi-farm.conf
COPY samadi-farm-backend/deployment/Caddyfile /etc/caddy/Caddyfile
COPY samadi-farm-backend/deployment/entrypoint.sh /usr/local/bin/samadi-farm-entrypoint
RUN chmod +x /usr/local/bin/samadi-farm-entrypoint \
    && mkdir -p /data/media

EXPOSE 80 443
VOLUME ["/data"]
ENTRYPOINT ["/usr/local/bin/samadi-farm-entrypoint"]
