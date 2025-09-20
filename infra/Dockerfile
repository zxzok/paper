FROM python:3.11-slim AS backend
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    wget \
    pandoc \
    latexmk \
    && rm -rf /var/lib/apt/lists/*

COPY infra/scripts/install-texlive.sh /tmp/install-texlive.sh
RUN bash /tmp/install-texlive.sh && rm -rf /tmp/install-texlive.sh /tmp/install-tl-*

WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir fastapi==0.111.0 uvicorn[standard]==0.29.0 httpx==0.27.0 jinja2==3.1.4 \
    celery==5.3.6 redis==5.0.1 python-dotenv==1.0.1 rapidfuzz==3.6.1 python-multipart==0.0.9

COPY backend ./backend
COPY templates ./templates
COPY infra/pandoc ./infra/pandoc

EXPOSE 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
