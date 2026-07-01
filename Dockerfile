FROM python:3.11-slim

# System deps: psycopg2 needs libpq; CLIP/transformers fine on slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bake the CLIP model into the image so cold starts are fast on Render
# (otherwise it downloads ~600MB from HuggingFace on every fresh boot)
ENV HF_HOME=/app/.hf_cache
RUN python -c "from transformers import CLIPModel, CLIPProcessor; \
    CLIPModel.from_pretrained('openai/clip-vit-base-patch32'); \
    CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')"

# Copy the app (frontend/dist is already built and committed)
COPY . .

# Render provides $PORT at runtime; default to 8000 for local docker run
ENV PORT=8000
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
