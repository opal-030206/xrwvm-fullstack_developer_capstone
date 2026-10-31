# Cars Dealership - Django + React container image
#
#   docker build -t cars-dealership .
#   docker run -p 8080:8080 -e SENTIMENT_SERVICE_URL=http://sentiment:8080 cars-dealership
#
# Stage 1 compiles the React frontend with Node, stage 2 runs Django on gunicorn
# and serves the compiled bundle plus the static pages through WhiteNoise.
FROM node:20-alpine AS frontend
WORKDIR /build/server/frontend
COPY server/frontend/package.json server/frontend/package-lock.json ./
RUN npm ci
COPY server/frontend/ ./
RUN npm run build

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CAR_DEALERSHIP_DEBUG=0 \
    PORT=8080

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY manage.py ./
COPY server ./server
COPY --from=frontend /build/server/frontend/dist ./server/frontend/dist

RUN python manage.py collectstatic --noinput

EXPOSE 8080

# The SQLite database lives inside the container, so the demo data is seeded on
# every cold start. Mount a volume over /app if you need it to persist.
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py seed_data && gunicorn server.wsgi:application --bind 0.0.0.0:${PORT} --workers 2 --timeout 120"]
