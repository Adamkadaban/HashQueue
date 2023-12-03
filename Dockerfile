FROM debian:latest

RUN apt-get update && \
    apt-get install -y wget python3 python3-pip hashcat hcxtools

RUN mkdir -p /opt/HashQueue && \
    mkdir -p /usr/share/wordlists && \
	mkdir -p /opt/HashQueue/data

COPY main.py /opt/cracker/main.py
COPY rockyou.txt /usr/share/wordlists

RUN pip3 install gunicorn

WORKDIR /opt/HashQueue

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
