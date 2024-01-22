FROM python:3.9

# RUN apk add --no-cache gcc musl-dev linux-headers

WORKDIR /app

COPY . .

RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

ENV PYTHONUNBUFFERED=1


CMD python server.py