FROM python:3.11-alpine

RUN apk update && apk add --no-cache \
    bash \
    coreutils \
    findutils \
    grep \
    sed \
    gawk \
    procps

WORKDIR /app

COPY . .

RUN chmod +x shell.py

CMD ["python3", "shell.py"]