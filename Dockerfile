# For more information, please refer to https://aka.ms/vscode-docker-python
FROM ubuntu/postgres:latest
RUN apt-get update && apt-get install -y python3 python3-pip
RUN apt-get install -y git


EXPOSE 5000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

RUN git clone https://github.com/metadata-research/yamz.git
WORKDIR /app


# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
#RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
#USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["flask", "run", "-h", "0.0.0.0", "-p", "5000", "--app", "yamz.py"]
