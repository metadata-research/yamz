# For more information, please refer to https://aka.ms/vscode-docker-python

FROM ubuntu:focal


ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=America/New_York


RUN apt-get update && apt-get install -y tzdata python3 python3-pip git
ARG TZ=Etc/UTC
RUN apt-get install -y postgresql-12

RUN git clone https://github.com/metadata-research/yamz.git

# RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /yamz

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


#RUN command="initdb -D /var/lib/postgresql/data" && \
#su - postgres -c "$command"
# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
#RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
# USER appuser

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

ENV FLASK_APP=yamz.py

# Install pip requirements
COPY config.py /yamz/config.py
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt


RUN rm /var/run/postgresql/.s.PGSQL.5432.lock
# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug

ENTRYPOINT service postgresql start && psql -f yamz.sql && python3 -m flask run -h 0.0.0.0 -p 5000

