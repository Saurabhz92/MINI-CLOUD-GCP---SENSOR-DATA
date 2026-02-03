FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for psycopg2 (if not using binary, but binary is safer for small alpine, slim is debian)
# psycopg2-binary handles it, but sometimes libpq-dev is needed. 
# For slim imagery, it's usually okay or we add:
# RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY worker.py .

CMD ["python", "worker.py"]
