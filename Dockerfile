FROM python:3.7.4-slim-buster
LABEL maintainer="Frank Rosendorf <frank.rosendorf1@gmail.com>"

WORKDIR /app

COPY requirements.txt requirements.txt

ENV BUILD_DEPS="build-essential" \
    APP_DEPS="curl libpq-dev"

RUN apt-get update \
  # install build and app deps
  && apt-get install -y ${BUILD_DEPS} ${APP_DEPS} --no-install-recommends \
  && pip install -r requirements.txt \
  # next two lines remove unnecessary files
  && rm -rf /var/lib/apt/lists/* \
  && rm -rf /usr/share/doc && rm -rf /usr/share/man \
  # remove the build deps as they are no longer needed in the image
  && apt-get purge -y --auto-remove ${BUILD_DEPS} \
  # remove cache related files
  && apt-get clean

# set some default env variables in the image
ARG FLASK_ENV="production"
ENV FLASK_ENV="${FLASK_ENV}" \
    PYTHONUNBUFFERED="true"

COPY . .

RUN pip install --editable .

EXPOSE 8000

CMD ["gunicorn", "-c", "python:config.gunicorn", "vidme.app:create_app()"]