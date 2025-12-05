ARG PYTHON_VERSION=3.13
ARG REPO_PREFIX=""
FROM ${REPO_PREFIX}python:${PYTHON_VERSION}-alpine AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ARG http_proxy
ARG https_proxy

WORKDIR /app

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

curl -LsSf https://astral.sh/uv/install.sh | sh \

# Install the dependencies
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
#    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt


COPY sircyl sircyl

RUN chown -R appuser .

USER appuser

EXPOSE 5000

# Run the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers=4", "--log-level=debug", "--timeout", "600", "--capture-output", "sircylworkflow.cli.restserver"]
#CMD ["flask", "--app", "sircyl.restserver.entrypoints.app:app", "run", "--host=0.0.0.0"]
