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


RUN apk update && \
    apk add --no-cache --virtual build-deps \
        make gcc \
        python3-dev musl-dev libffi-dev openssl-dev && \
    python3 -m ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools wheel


ADD . /app
WORKDIR /app


RUN pip install pipenv && \
    pipenv lock -r > requirements.txt && \
    pipenv run python setup.py bdist_wheel && \
    pipenv run pip wheel --wheel-dir=dist -r requirements.txt

##############################################################################
# Step 2: build the Flask app image
##############################################################################
FROM python:3.7-alpine
COPY --from=build /app/dist/*.whl dist/

RUN apk update && \
    apk add python3-dev && \
    python3 -m ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools wheel && \
    python3 -m pip install --find-links . --no-index dist/*.whl && \
    rm -r dist


ENV FLASK_APP windninja_server/windninjaweb/app.py

RUN adduser -D ninja
USER ninja

EXPOSE 5000
ENTRYPOINT ["/app/bin/boot.sh"]
