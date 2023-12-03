FROM debian:latest

RUN apt-get update && \
    apt-get install -y wget python3 python3-pip hashcat hcxtools python3-gunicorn python3-flask

RUN mkdir -p /opt/HashQueue/data && \
    mkdir -p /usr/share/wordlists

COPY main.py /opt/HashQueue/
COPY rockyou.txt /usr/share/wordlists/

WORKDIR /opt/HashQueue

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:5000", "main:app"]
