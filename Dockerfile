FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY backEnd/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Keep the package folder so imports like `from backEnd...` work.
COPY backEnd /app/backEnd

# Static frontend served by FastAPI (mounted from /app/frontEnd)
COPY frontEnd /app/frontEnd
EXPOSE 8000

CMD ["uvicorn", "backEnd.main:app", "--host", "0.0.0.0", "--port", "8000"]
