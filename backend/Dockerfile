FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    libffi-dev \
    python3-dev \
    libpq-dev \
    curl \
    postgresql-client \
    ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY wait-for-db.sh /wait-for-db.sh
RUN chmod +x /wait-for-db.sh

EXPOSE 8000

CMD ["/wait-for-db.sh", "postgres", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
