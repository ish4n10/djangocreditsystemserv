FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

ENV DB_NAME=postgres \
    DB_USER=postgres \
    DB_PASSWORD=postgres \
    DB_HOST=localhost \
    DB_PORT=5432

EXPOSE 8000

# Run migrations then start server
CMD ["/bin/sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput || true && python manage.py runserver 0.0.0.0:8000"]


