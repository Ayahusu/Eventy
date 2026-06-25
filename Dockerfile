FROM ghcr.io/astral-sh/uv:latest AS uv

FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /event

COPY --from=uv /uv /uvx /bin/

COPY requirements.txt .

RUN uv pip install --system -r requirements.txt

COPY . .

RUN useradd -m django \
    && chown -R django:django /event

USER django

EXPOSE 8000

CMD ["gunicorn", "eventy.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]