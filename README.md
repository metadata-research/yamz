
# YAMZ Metadata Dictionary

This is the README for the YAMZ metadictionary and includes instructions for
deploying on a local machine for testing and on a Linux based environment for a
scalable production version (coming soon). 

The current application requires the use of a postgres database to support full text search. 

The following is an example configuration. You can substitute your own db names and users

## Install

1. Install postgres. Installation instructions may vary depending on the platform.

[postgres downloads](https://www.postgresql.org/download/)


2. Edit a postgres user.

    sudo -u postgres psql template1

    postgres=# alter user postgres with encrypted password 'PASS';

On a mac
    createuser -d postgres
    psql -c "alter user contributor with encrypted password 'PASS'"


3. Create a database in psql

(the installation should create a unix user postgres so something like sudo -u postgres psql). On a mac psql -U postgres -c 'create database yamz with owner postgres'

postgres=# create database yamz with owner postgres;


4. Grant priveleges to that user

postgres=# grant all privileges on database yamz to postgres;

mac: psql -c "grant all priveleges on database yamz to postgres"


5. Clone the repository

git clone https://github.com/metadata-research/yamz.git

6. switch to the yamz directory

cd yamz

7. Create a python virtual environment

virtualenv env

[on a mac](https://gist.github.com/pandafulmanda/730a9355e088a9970b18275cb9eadef3) external

8. Activate

source env/bin/activate

9.  install the python dependencies

pip install -r requirements.txt


10.  create a config.py file in the root directory using the example in the /stubs directory

cp stubs/_config.py config.py

Make sure to specify both orcid and google credentials and the username and password of the database you created. You can get these credentials here for [google](https://console.cloud.google.com/apis/credentials) and from orcid under the developer tab in your profile. [Sandbox](https://console.cloud.google.com/apis/credentials)

From the config.py file:
    OAUTH_CREDENTIALS = {
        "google": {
            "id": "<your-client-id>",
            "secret": "<your-client-secret>",
        },
        "orcid": {
            "id": "<your-client-id>",
            "secret": "<your-client-secret>",
        },
    }

    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("SQL_ALCHEMY_DATABASE_URI")
        or "postgresql://contributor:PASS@localhost/yamz"
    )

11.  set the FLASK_APP variable

    export FLASK_APP=yamz.py

12.  On the first run create the db

    flask db init

    flask db migrate

(an error had come up here sometimes and the workaround for now is
    
    flask db revision --rev-id xxxxxxxxxx

    flask db upgrade

13. Run the app

if you want to use a different port for the dev server

    export FLASK_RUN_PORT=xxxx

If you want to run in development mode

    export FLASK_ENVIRONMENT=development

    flask run

Note that when working in dev mode, the google authorized urls must allow access on the port for authentication to work. You set these in the [console](https://console.cloud.google.com/apis/credentials).  Orcid authentication similarly will only work if the url is pre-authorized.



## Import legacy entries

    python admin.py addall

for just users

    python admin.py addusers

for just terms

    python admin.py addterms

you must add users before terms to preserve the pk based relationships