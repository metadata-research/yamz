
# YAMZ Metadictionary

This is the README for the YAMZ vocabulary builder for data and metadata.
It includes instructions for deploying on a local machine for testing and on
a Linux-based environment for a scalable production version (coming soon). 

The current application requires the use of a postgres database to support full-text search. 

The following is an example configuration. You can substitute your own db names and users.

## Install

1. Install postgres. Installation instructions may vary depending on the platform.

[postgres downloads](https://www.postgresql.org/download/)

On macOS, you can use homebrew:
    
    brew install postgresql

Make sure the postgres server is running. You may want to configure your
computer so that the server starts automatically on reboot. On macOS, for
example:

    brew services start postgresql

on Ubuntu:
    
    ## Postgres default users
The default unix admin user, postgres, needs a password assigned in order to connect to a database. To set a password:

Enter the command:
   `sudo passwd postgres`

You will get a prompt to enter your new password.

Close and reopen your terminal.
(parallel to the postgres user 'postgres'), allowing something like

    sudo -u postgres psql

    postgres=# create database yamz with owner postgres;

## Postgres authentication configuration
Configure the authentication method for postgres and all other users connecting locally
In `/etc/postgresql/14/main/pg_hba.conf` change "peer" to md5 for the administrative account and local unix domain socket

    # TYPE  DATABASE        USER            ADDRESS                 METHOD
    # "local" is for Unix domain socket connections only
    local   all             all                                     md5
    # IPv4 local connections:
    host    all             all             127.0.0.1/32            md5

Next, we want to only be able to connect to the database from the local machine

In `/etc/postgresql/14/main/postgresql.conf`

uncomment the line

`listen_addresses = 'localhost'`

Restart the postgres server

`sudo service postgresql restart`

Finally, log back in to postgres to create the database,

Add a db password for the user 'postgres'. 
   
    `sudo -u postgres psql template1`
    `postgres=# alter user postgres with encrypted password 'PASS';`

`sudo -u postgres psql`

`postgres=# create database yamz with owner postgres;`

`postgres-# \q`

On macOS:

    createuser -d postgres
    psql -U postgres -c "alter user postgres with encrypted password 'PASS'"

On macOS:

    psql -U postgres -c 'create database yamz with owner postgres'

4. Placeholder


5. Clone the repository

    `git clone https://github.com/metadata-research/yamz.git`

6. switch to the yamz directory

    `cd yamz`

7. Create a python 3 virtual environment

    `virtualenv env`

On macOS, you may have to first install python3 and virtualenv (https://gist.github.com/pandafulmanda/730a9355e088a9970b18275cb9eadef3)

    brew install python3
    pip3 install virtualenv
    virtualenv env

8. Activate the virtual environment:

    `source env/bin/activate`

9.  Install the Python dependencies:

    `pip install -r requirements.txt`


10. Modify the `\_config.py` file in the root directory with the appropriate credentials and change the name to `config.py` (remove the leading underscore). `config.py` is included in `.gitignore` so the modified file should not be pushed to the repository.

Make sure to specify both orcid and google credentials and the username and password of the database you created. You can get these credentials here for [google](https://console.cloud.google.com/apis/credentials) and from ORCID under the developer tab in your profile. [Sandbox](https://console.cloud.google.com/apis/credentials)

From the `config.py` file:

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

11. Set the `FLASK_APP` variable:

    `export FLASK_APP=yamz.py`

12. On the first run, create the db:

    `flask db init`

On subsequent runs:

    flask db migrate
    flask db upgrade     

13. Run the app

If you want to use a different port for the dev server, set FLASK_RUN_PORT.
For example, on macOS the default Flask port (5000) can conflict with the
default AirPlay Receiver port, so you might run Flask on 5001 instead:

    export FLASK_RUN_PORT=5001

If you want to run in development mode (which sends error messages to the
console):

    export FLASK_ENVIRONMENT=development
    flask run

Note that when working in dev mode, the Google-authorized URLs must allow 
access on the port for authentication to work. You set these in the 
[console](https://console.cloud.google.com/apis/credentials). 
ORCID authentication similarly will only work if the URL is pre-authorized.


## Import Legacy Entries

    It is no longer necessary to run the scripts to import legacy entries. Please follow the instructions
    for backups below to import the entries into a new instance of yamz. 

## OAuth Credentials and appkey

YAMZ uses Google for third party authentication (OAuth-2.0) management of
logins. Visit https://console.cloud.google.com to set this service up
for your instance. Navigate to something like APIs and Services -> Credentials
and select whatever lets you create a new OAuth client ID.  For local
configuration, supply these answers:

    Application type . . . . . . . . . . Web application

    Authorized javascript origins  . . . https://localhost:5000 # note that the Credential API will not permit publishing the app with non-https redirects so it would be necessary to create a certificate for the machine running a dev instance of NGINX in order to test the Google authentication component locally
                                         https://localhost
                                         https://domain.name

    Authorized redirect URI  . . . . . . https://localhost:5000/g_authorized
                                         https://localhost/g_authorized
                                         https://domain.name/g_authorized

The credentials minus the port is for when the proxy web server is set up, you are no longer using the flask 
development server, and have set up https on a named server. You can also serve the application locally using 
HTTPS by invoking uwsgi and the ini file from within the yamz directory `uwsgi yamz_local.ini` but you will need 
to generate an ssl certificate for the localhost and add it to your browser or OS store.

## Deploying to Production

Create a `yamz.ini` file in the yamz directory. There is a template in the repository

    [uwsgi]
    module = yamz:app

    master = true
    processes = 5

    socket = yamz.sock
    chmod-socket = 660
    vacuum = true
    
    die-on-term = true

Create a unit file `yamz.service` within the `/etc/systemd/system` directory. _usr1_ is a stand-in for the username 
that is associated with the running instance of your web server.
  
    [Unit]
    Description=uWSGI instance to serve yamz
    After=network.target
    
    [Service]
    User=usr1 
    Group=www-data
    WorkingDirectory=/home/usr1/yamz
    ExecStart=uwsgi --ini yamz.ini

    [Install]
    WantedBy=multi-user.target

Start the service:

`sudo systemctl start yamz`

Enable the service so that it starts at boot:

`sudo systemctl enable yamz`

Check the status:

`sudo systemctl status yamz`

YAMZ is now running, waiting for requests on the socket file.

## Configuring Nginx to Proxy Requests

Create a new server block configuration file in Nginx's sites-available directory.

For example ` sudo nano /etc/nginx/sites-available/yamz`

    server {
        listen 80;
        server_name yamz.link www.yamz.link;
        location / {
            include uwsgi_params;
            uwsgi_pass unix:/home/usr1/yamz/yamz.sock;
        }
    }


Save and close the file when you are finished.

To enable the Nginx server block configuration, link the file to the sites-enabled directory:

`sudo ln -s /etc/nginx/sites-available/yamz /etc/nginx/sites-enabled`


Remove the default site or it will block the proxying.

`sudo unlink /etc/nginx/sites-enabled/default`

Test for syntax errors.

`sudo nginx -t`

The YAMZ prototype is currently hosted at http://yamz.link

Make sure the user in the /etc/nginx/nginx.conf file is the user you want to run the project under

Restart nginx.

`sudo systemctl restart nginx`

## Secure the Application

You can do this anyway you like, but currently it is with Certbot and its Nginx plugin

The Nginx plugin will take configure Nginx and reload the config when necessary. To use it

`sudo certbot --nginx -d yamz.link -d www.yamz.link`

Make sure there is a generic type a record and one for www for your domain.

Certbot will ask you whether you wish to redirect all http traffic to https (removing http access).

## Backups
Backup on production
`pg_dump -C -Fp -f yamz.sql -U postgres yamz`

This will create a yamz.sql file that is portable.

For example, to restore from a given daily backup:

    service yamz stop
    dropdb -U postgres yamz
    psql -U postgres -f yamz_2023-05-11.sql

To update the yamz_dev database from current production database:

    service yamz stop
    psql -U postgres
    postgres=# CREATE DATABASE yamz_dev WITH TEMPLATE yamz

## Development Environment
The dev environment for the current version of YAMZ is a direct copy of the production environment, currently located on the same server but in a different directory. (~/yamz_dev). There are several differences. 

The UNIX socket file must have a different name than yamz.sock in the yamz.ini file. Currently, it is called yamz_dev.sock

The `SQLALCHEMY_DATABASE_URI` points to a copy of the yamz database called yamz_dev which is not in syc with the main database. To sync it you can restore a backup copy with the yamz_dev name as described in 'Backups' above.

There is a UNIX service called yamz_dev running that starts the uwsgi workers for the dev site. It is a copy of the yamz.service, just with a different name.

The same git branch (deploy) exists in this dev directory so changes here will come as a pull request to 'deployment.' This is a shortcut that should be addressed.


## Reinstalling YAMZ Environment
1. Make a copy of the config file. You will need it once you pull the repository from GitHub.
1. If you plan on restoring the database from the same computer, execute the command to save the db to a file.
1. `sudo pg_dump -C -Fp -f yamz.sql -U postgres yamz`
   1. This will create a file, yamz.sql. Save this or obtain the file from the production environment.
1. Run psql as the postgres user `sudo -u postgres psql`
1. Drop the yamz database `DROP DATABASE YAMZ`
1. Restore from the backup `psql -U postgres -f yamz.sql`
1. In an empty directory, clone the deployment repository.
1. Copy the config file into the top-level directory.
1. Start YAMZ via `flask run`
1. If you want to use migrations, first delete the alembic version from the restored db.
1. `flask db init`
