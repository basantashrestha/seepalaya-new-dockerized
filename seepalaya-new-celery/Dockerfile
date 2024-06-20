FROM python:3.11.4-alpine3.18

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app
COPY ./src/requirements/requirements_dev.txt /usr/src/app
COPY ./src/requirements/base.txt /usr/src/app


RUN pip install --upgrade pip && \
    apk update && \
    apk add postgresql-dev gcc python3-dev musl-dev jpeg-dev zlib-dev && \
    pip install -r requirements_dev.txt
    
COPY ./src/.env /usr/src/app
RUN mkdir /usr/src/app/logs

COPY ./src /usr/src/app/


