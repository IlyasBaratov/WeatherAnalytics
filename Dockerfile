# syntax=docker/dockerfile:1

ARG BASE_IMAGE

# App image: code + assets only (small delta on top of the base image).
# This Dockerfile expects BASE_IMAGE to already contain OS + Python dependencies.
FROM ${BASE_IMAGE}

WORKDIR /app

# Keep the package folder so imports like `from backEnd...` work.
COPY backEnd /app/backEnd

# Static frontend served by FastAPI (mounted from /app/frontEnd)
COPY frontEnd /app/frontEnd

EXPOSE 8000

CMD ["uvicorn", "backEnd.main:app", "--host", "0.0.0.0", "--port", "8000"]
