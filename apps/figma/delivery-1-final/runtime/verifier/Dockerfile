FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY verifier /workspace/verifier
COPY scripts /workspace/scripts
RUN mkdir -p /workspace/output/logs /workspace/output/scores

CMD ["sleep", "infinity"]
