
# YAMZ Metadata Dictionary

This is the README for the YAMZ metadictionary and includes instructions for
deploying on a local machine for testing and on a Linux based environment for a
scalable production version (coming soon). 

The current application requires the use of a postgres database to support full text search. 

The following is an example configuration. You can substitute your own db names and users

## Install

1. Install postgres. Installation instructions may vary depending on the platform.

[postgres downloads](https://www.postgresql.org/download/)

On a mac you can use homebrew
    brew install postgresql

Make sure the postgres server is running. You may want to configure your
computer so that the server starts automatically on reboot. On a mac, for
example,
    brew services start postgresql

2. Add a password for the user 'postgres'.

    sudo -u postgres psql template1

    postgres=# alter user postgres with encrypted password 'PASS';

On a mac
    createuser -d postgres
    psql -U postgres -c "alter user postgres with encrypted password 'PASS'"

3. Create a yamz database using the psql client.

On Linux, the installation should create a system user 'postgres'
(parallel to the postgres user 'postgres'), allowing something like

    sudo -u postgres psql
    postgres=# create database yamz with owner postgres;

On a mac
    psql -U postgres -c 'create database yamz with owner postgres'

4. Placeholder


5. Clone the repository

    git clone https://github.com/metadata-research/yamz.git

6. switch to the yamz directory

    cd yamz

7. Create a python 3 virtual environment

    virtualenv env

On a mac you may have to first install python3 and virtualenv (https://gist.github.com/pandafulmanda/730a9355e088a9970b18275cb9eadef3)

    brew install python3
    pip3 install virtualenv
    virtualenv env

8. Activate

    source env/bin/activate

9.  install the python dependencies

    pip install -r requirements.txt


10. Modify the \_config.py file in the root directory with the appropriate credentials and change the name to config.py (remove the leading underscore). config.py is included in git ignore so the modified file should not be pushed to the repository

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

11. Set the FLASK_APP variable

    export FLASK_APP=yamz.py

12. On the first run create the db

    flask db init

On not-the-first run do
    flask db migrate

    flask db upgrade     

13. Run the app

if you want to use a different port for the dev server

    export FLASK_RUN_PORT=xxxx

If you want to run in development mode (which sends error messages to the
console),

    export FLASK_ENVIRONMENT=development

    flask run

Note that when working in dev mode, the google authorized urls must allow access on the port for authentication to work. You set these in the [console](https://console.cloud.google.com/apis/credentials).  Orcid authentication similarly will only work if the url is pre-authorized.


## Import legacy entries

    It is no longer necessary to run the scripts to import legacy entries. Please follow the instructions
    for backups below to import the entries into a new instance of yamz. 

## OAuth Credentials and appkey

YAMZ uses Google for third party authentication (OAuth-2.0) management of
logins. Visit https://console.cloud.google.com to set this service up
for your instance. Navigate to something like APIs and Services -> Credentials
and select whatever lets you create a new OAuth client ID.  For local
configuration, supply these answers:

    Application type . . . . . . . . . . Web application

    Authorized javascript origins  . . . http://localhost:5000
                                         http://localhost
                                         https://domain.name

    Authorized redirect URI  . . . . . . http://localhost:5000/g_authorized
                                         https://localhost/g_authorized
                                         https://domain.name/g_authorized

The credentials minus the port is for when the proxy web server is set up and you are no longer using the flask development server and have set up https on a named server. You can also serve the application locally using https by invoking uwsgi and the ini file from within the yamz directory `uwsgi yamz_local.ini` but you will need to generate an ssl certificate for the localhost and add it to your browser or os store.

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

Create a unit file `yamz.service` within the `/etc/systemd/system` directory. _usr1_ is a standin for the username that is associated with the running instance of your webserver.
  
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

Start the service.

`sudo systemctl start yamz`

Enable it so it starts at boot.

`sudo systemctl enable yamz`

Check the status.

`sudo systemctl status yamz`

Yamz is now running, waiting for requests on the socket file

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


Save and close the file when you’re finished.

To enable the Nginx server block configuration, link the file to the sites-enabled directory:

`sudo ln -s /etc/nginx/sites-available/yamz /etc/nginx/sites-enabled`


Remove the default site or it will block the proxying.

`sudo unlink /etc/nginx/sites-enabled/default`

test for syntax errors

`sudo nginx -t`

The YAMZ prototype is currently hosted at http://yamz.link

make sure the user in the /etc/nginx/nginx.conf file is the user you want to run the project under

Restart nginx.

`sudo systemctl restart nginx`

## Secure the application

You can do this anyway you like, but currently it is with Certbot and its Nginx plugin

The Nginx plugin will take configure Nginx and reload the config when necessary. To use it

`sudo certbot --nginx -d yamz.link -d www.yamz.link`

Make sure there is a generic type a record and one for www for your domain.

Certbot will ask you whether you wish to redirect all http traffic to https (removing http access).

## Backups
Backup on production
`pg_dump -C -Fp -f yamz.sql -U postgres yamz`

A fairly recent copy is also available in the git repository

Restore on development
`psql -U postgres -f yamz.sql'
