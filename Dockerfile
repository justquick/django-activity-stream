FROM python:3.9

ENV PYTHONUNBUFFERED 1
ENV LC_ALL=C.UTF-8

#
# RUN apt-get -y update && apt-get -y --no-install-recommends install \
#     build-essential \
#     gcc \
#     gettext \
#     python3-dev \
#     python3-venv \
#     && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/* /usr/share/doc/* /usr/share/locale/* /usr/share/man/* && \
#     mkdir -p /app && \
#     (useradd -m app || true)


WORKDIR /app

ADD runtests/requirements.txt /app/

RUN pip install -r requirements.txt

ENV DJANGO_SETTINGS_MODULE settings

# *WARNING*: DO NOT "ADD . /app" because it would include the current settings in the base image, which is uploaded by
# CI to docker hub; Since the settings currently include secrets, this would leak our credentials!

EXPOSE 8000

CMD ["/app/manage.py", "runserver", "0.0.0.0:8000"]
