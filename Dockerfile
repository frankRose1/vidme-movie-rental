FROM python:3.6-slim

# for postgres database
RUN apt-get update && apt-get install -qq -y \
  build-essential libpq-dev --no-install-recommends

RUN mkdir /app
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

# for the CLI
RUN pip install --editable .

CMD gunicorn -b 0.0.0.0:8000 --access-logfile - "vidme.app:create_app()"