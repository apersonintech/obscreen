FROM python:3.9.17-alpine3.17

# Install ffmpeg and other dependencies
RUN apk add --no-cache gcc musl-dev sqlite-dev ntfs-3g ffmpeg build-base linux-headers

WORKDIR /app

COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "/app/obscreen.py"]
