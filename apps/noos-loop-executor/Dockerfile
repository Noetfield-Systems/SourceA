FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV NOOS_EXECUTOR_ROOT=/app
ENV PYTHONPATH=/app/apps/noos-loop-executor

# Bounded tick dependencies only — no full FBE image
COPY data/trigger-registry-v1.json data/trigger-registry-v1.json
COPY scripts/sandbox_health_sweep_v1.py scripts/sandbox_health_sweep_v1.py
COPY apps/noos-loop-executor/noos_loop_executor apps/noos-loop-executor/noos_loop_executor
COPY apps/noos-loop-executor/entrypoint.sh apps/noos-loop-executor/entrypoint.sh

RUN chmod +x apps/noos-loop-executor/entrypoint.sh

EXPOSE 8080
CMD ["apps/noos-loop-executor/entrypoint.sh"]
