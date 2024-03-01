FROM python:3.9.17-alpine3.17

RUN apk add --no-cache git chromium

RUN apk add --no-cache --virtual .build-deps git gcc musl-dev \
     && pip install flask pysondb-v2==2.1.0 \
     && apk del .build-deps gcc musl-dev

WORKDIR /app

COPY . .

ENTRYPOINT ["python", "/app/obscreen.py"]