FROM ubuntu:focal

ENV PYTHONUNBUFFERED 1
ENV LC_ALL=C.UTF-8
ARG DEBIAN_FRONTEND=noninteractive

# the base image is also built using this Dockerfile, so we have to reset this
USER root

RUN apt-get -y update && apt-get -y --no-install-recommends install \
    build-essential \
    gcc \
    gettext \
    python3-dev \
    python3-venv \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /usr/share/doc/* /usr/share/locale/* /usr/share/man/* && \
    mkdir -p /app && \
    (useradd -m app || true)

COPY --from=library/docker:latest /usr/local/bin/docker /usr/bin/docker
COPY --from=docker/compose:1.23.2 /usr/local/bin/docker-compose /usr/bin/docker-compose

WORKDIR /app

ADD runtests/requirements.txt /app/

USER app

ENV PATH /home/app/venv/bin:${PATH}

RUN python3 -m venv ~/venv && \
    pip install -r /app/requirements.txt

ENV DJANGO_SETTINGS_MODULE settings

# *WARNING*: DO NOT "ADD . /app" because it would include the current settings in the base image, which is uploaded by
# CI to docker hub; Since the settings currently include secrets, this would leak our credentials!

EXPOSE 8000

ENTRYPOINT ["/app/manage.py"]
