FROM ubuntu:focal


ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=America/New_York


RUN apt-get update && apt-get install -y tzdata python3 python3-pip git

RUN apt-get install -y postgresql-12

RUN git clone https://github.com/metadata-research/yamz.git


#TODO: RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /yamz


RUN chown -R postgres /yamz
USER postgres

RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/12/main/pg_hba.conf
RUN echo "listen_addresses='*'" >> /etc/postgresql/12/main/postgresql.conf

RUN /etc/init.d/postgresql start &&\
    psql --command "ALTER USER postgres WITH SUPERUSER PASSWORD 'PASS';" &&\
    createdb -O postgres yamz
# RUN psql -f yamz.sql


EXPOSE 5432 5000

WORKDIR /yamz


# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

ENV FLASK_APP=yamz.py

# Install pip requirements
COPY _config.py /yamz/config.py
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt


# this is leftover from the container setup I think. Maybe figure out how to shutdown there
RUN rm /var/run/postgresql/.s.PGSQL.5432.lock

COPY yamz.sql /yamz/

ENTRYPOINT service postgresql start && psql -f yamz.sql && python3 -m flask run -h 0.0.0.0 -p 5000

