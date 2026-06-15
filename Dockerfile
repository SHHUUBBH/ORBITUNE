FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY AI-ML/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY BACKEND/src ./src
COPY AI-ML /AI-ML

EXPOSE 7860

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "7860"]