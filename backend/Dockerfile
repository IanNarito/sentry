# backend/Dockerfile
FROM python:3.10-slim

# 1. Install System Dependencies (Nmap is critical here!)
RUN apt-get update && apt-get install -y \
    nmap \
    && rm -rf /var/lib/apt/lists/*

# 2. Set Work Directory
WORKDIR /app

# 3. Install Python Dependencies
# We copy just requirements first to cache the layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the Application Code
COPY . .

# 5. Default Command (Will be overridden by docker-compose)
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]