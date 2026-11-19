# API image (QR-PO-01): Python 3.13 on Alpine (fewer OS packages than Debian slim, see SEC-06 triage), dependencies pinned in requirements.txt, non-root user, healthcheck.
FROM python:3.13-alpine3.24

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Apply Alpine security fixes published after the base image was built (Trivy, SEC-06).
RUN apk upgrade --no-cache

WORKDIR /app
COPY requirements.txt .
# Runtime needs neither pip nor setuptools: removing them drops their bundled CVEs (Trivy, SEC-06).
RUN pip install -r requirements.txt && pip uninstall -y setuptools pip

COPY app ./app
RUN adduser -S -D -H -u 10001 api
USER 10001

EXPOSE 8000
# /api/health answers 200 only when the database answers (503 otherwise), so "healthy" means "can serve".
HEALTHCHECK --interval=5s --timeout=3s --start-period=10s --retries=5 \
  CMD ["python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=2).status == 200 else 1)"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
