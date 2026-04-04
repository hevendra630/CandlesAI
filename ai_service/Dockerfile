FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only torch first (smaller image)
RUN pip install --no-cache-dir torch==2.3.0 --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir fastapi==0.111.0 uvicorn[standard]==0.29.0 pydantic==2.7.1 \
    numpy==1.26.4 httpx==0.27.0 \
    tensorflow-cpu==2.16.1 \
    transformers==4.40.2

RUN mkdir -p /app/models

COPY . .

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
