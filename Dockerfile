FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOME=/home/appuser

WORKDIR /app

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/home/appuser" \
    --shell "/bin/sh" \
    --uid "${UID}" \
    appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["gunicorn", "app:app", "--bind=0.0.0.0:8000"]

# To build the image, run:
    # docker compose up --build
    # recreate by running:
    # docker compose up
# docker build -t tech-blog-world:latest . 
# To run the container, run:
# docker run -d -p 8000:8000 --env-file .env --