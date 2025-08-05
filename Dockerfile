FROM ubuntu:latest

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=America/New_York

RUN apt-get update && apt-get install -y \
    tzdata python3 python3-pip git postgresql postgresql-client

RUN git clone https://github.com/metadata-research/yamz.git

WORKDIR /yamz

COPY _config.py /yamz/config.py
COPY requirements.txt .
COPY yamz.sql /yamz/
RUN python3 -m pip install --no-cache-dir -r requirements.txt

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=yamz.py

RUN chown -R postgres /yamz
USER postgres

# This will dynamically find the PostgreSQL version
RUN VERSION=$(ls /etc/postgresql/) && \
    echo "host all all 0.0.0.0/0 md5" >> /etc/postgresql/$VERSION/main/pg_hba.conf && \
    echo "listen_addresses='*'" >> /etc/postgresql/$VERSION/main/postgresql.conf

USER root

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
EXPOSE 5432 5000
ENTRYPOINT ["/entrypoint.sh"]