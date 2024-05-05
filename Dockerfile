FROM python:3.9.17-alpine3.17

RUN apk add --no-cache git chromium \
    && apk add --no-cache --virtual .build-deps git gcc musl-dev

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt && apk del .build-deps gcc musl-dev

ENTRYPOINT ["python", "/app/obscreen.py"]
