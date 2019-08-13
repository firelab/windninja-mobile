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


RUN rm -rf /var/cache/apk && rm -rf /tmp/* \
 && mkdir /var/cache/apk

#RUN echo "ipv6" >> /etc/modules

RUN apk update \
    && apk add --no-cache --virtual build-deps make gcc python3-dev musl-dev libffi-dev openssl-dev


ADD . /app
WORKDIR /app


RUN pip install pipenv \
 && pipenv lock -r > requirements.txt \
 && pipenv run python setup.py bdist_wheel

##############################################################################
# Step 2: build the Flask app image
##############################################################################
FROM python:3.7-alpine
COPY --from=build /app/dist/*.whl .

RUN apk update \
 && apk add python3-dev python3-pip python3-wheel \
 && python3 -m pip install *.whl \
 && apk del python3-wheel python3-pip 


ENV FLASK_APP windninja_server/windninjaweb/app.py

RUN adduser -D ninja
#RUN chown -R ninja:ninja ./
USER ninja

EXPOSE 5000
ENTRYPOINT ["./bin/boot.sh"]
