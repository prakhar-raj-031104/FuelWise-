FROM python:3.12-slim

WORKDIR /code

# Install deps first for better layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Ratings are written here; mount a volume at this path to persist them.
ENV RATING_LOG=/data/mess_menu_ratings.jsonl
RUN mkdir -p /data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
