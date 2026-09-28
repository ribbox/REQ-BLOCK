FROM python:3.12-alpine

WORKDIR /app

# No external pip deps – stdlib only
COPY server.py /app/server.py

RUN mkdir -p /data && adduser -D -u 1000 appuser \
    && chown -R appuser:appuser /data /app

USER appuser

ENV HOST=0.0.0.0 \
    PORT=8080 \
    DATA_FILE=/data/project.json \
    CORS_ORIGIN=*

EXPOSE 8080

VOLUME ["/data"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -qO- http://127.0.0.1:8080/health || exit 1

CMD ["python", "-u", "server.py"]
