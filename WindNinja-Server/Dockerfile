##############################################################################
# Step 1: Build all dependencies into .whl files
# 
# Dependencies will be removed in the second stage to reduce the total 
# image size
##############################################################################
FROM python:3.7-alpine as build

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIPENV_VENV_IN_PROJECT 1

ADD requirements.txt /app/
WORKDIR /app

RUN apk update && \
    apk add --no-cache --virtual build-deps \
        make gcc \
        python3-dev musl-dev libffi-dev openssl-dev && \
    python3 -m ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools wheel


ADD . /app

RUN pip wheel --wheel-dir=dist -r requirements.txt

##############################################################################
# Step 2: build the Flask app image
# 
# Uses the wheels created from the first step to reduce the
# build times and remove the need to store the source directory
# in the image.
##############################################################################
FROM ubuntu:bionic

WORKDIR /app
COPY --from=build /app/dist/*.whl dist/
COPY --from=build /app/bin /app/bin

RUN set -xe \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt update -q && \
    apt install -y -q python3.7 && \
    python3.7 -m ensurepip && \
    python3.7 -m pip install --user --no-cache --upgrade pip setuptools wheel && \
    python3.7 -m pip install --user --find-links . --no-index dist/*.whl && \
    apt remove -y python3-pip python3-wheel && \
    apt autoremove -y && \
    apt clean -y && \
    rm -r dist && \
    rm -rf /var/lib/apt/lists/* && \
    useradd ninja --no-create-home --user-group

USER ninja

ENV FLASK_APP windninja_server.windninjaweb.app

EXPOSE 5000
ENTRYPOINT ["/app/bin/boot.sh"]
