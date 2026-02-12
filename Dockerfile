FROM python:3.13-slim-bookworm

WORKDIR /usr/src/recipehub

RUN apt-get update \
    && apt-get install -y netcat-openbsd \
    && pip install --upgrade pip \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "recipehub.wsgi:application"]