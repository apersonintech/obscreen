FROM python:3.9.17-alpine3.17

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "/app/obscreen.py"]
