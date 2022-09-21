FROM python:3.8

EXPOSE 5000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Set the location of the ini file
# ENV UWSGI_INI /app/yamz.ini

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app


# FROM postgres:12
# USER postgres

# Restore the database from a backup
# RUN echo "psql - U postgres -f /configs/yamz.sql"

# copy the application configuration file
# COPY ./configs/yamz.ini /app/yamz.ini

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["flask", "run"]
