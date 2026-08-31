FROM python:3.11-slim

# Install ffmpeg, curl, unzip and Deno
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL https://deno.land/install.sh | sh -s -- -y

ENV DENO_INSTALL="/root/.deno"
ENV PATH="$DENO_INSTALL/bin:$PATH"

# Create a user with UID 1000 for Hugging Face Spaces compatibility
RUN useradd -m -u 1000 user && \
    mkdir -p /app && \
    chown -R user:user /app && \
    chmod -R 777 /root/.deno

WORKDIR /app

# Copy backend requirements and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ /app/backend/
RUN chown -R user:user /app

USER user
ENV PYTHONPATH=/app/backend
EXPOSE 7860 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
