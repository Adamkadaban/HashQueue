FROM debian:latest

RUN apt-get update && \
    apt-get install -y wget p7zip-full python3 python3-pip hcxdumptool

WORKDIR /usr/share/hashcat

RUN wget https://github.com/hashcat/hashcat/releases/download/v6.2.6/hashcat-6.2.6.7z && \
    7z x hashcat-6.2.6.7z && \
    rm hashcat-6.2.6.7z

RUN ln -s /usr/share/hashcat/hashcat-6.3.6/hashcat.bin /bin/hashcat

RUN mkdir -p /opt/HashQueue && \
    mkdir -p /usr/share/wordlists
	mkdir -p /opt/HashQueue/data

COPY main.py /opt/cracker/main.py
COPY rockyou.txt /usr/share/wordlists

RUN pip3 install gunicorn

WORKDIR /opt/HashQueue

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8000", "main:app"]
