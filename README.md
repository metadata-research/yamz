
# YAMZ Metadata Dictionary

This is the README for the YAMZ metadictionary and includes instructions for
deploying on a local machine for testing and on a Linux based environment for a
scalable production version. These assume a Ubuntu GNU/Linux environment, but
should be easily adaptable to any system; YAMZ is written in Python and uses
only cross-platform packages.

Authored by Chris Patton.

Updated 2 November 2017 (Dillon Arevalo).

Last updated 21 July 2021 Christopher Rauch (cr625)

YAMZ was formerly known as SeaIce, so the database tables and API use names based on "SeaIce".

## Prerequisites

* PostgreSQL

## Installing Components from Ubuntu Repositories

Update Ubuntu package list

`sudo apt update`

Once the packages have been updated install PostgreSQL and the -contrib packackage

`sudo apt install postgresql postgresql-contrib`

## Postgress default users

The default unix admin user, postgres, needs a password assigned in order to connect to a database. To set a password:

1. Enter the command:
   `sudo passwd postgres`
2. You will get a prompt to enter your new password.
3. Close and reopen your terminal.


To run PostgreSQL with psql shell:

1. Start your postgres service:

`sudo service postgresql start`

2. Connect to the postgres service and open the psql shell:

`sudo -u postgres psql template1`

Once you have successfully entered the psql shell, you will see your command line change to look like this:

`template1=#`

Postgres psql requires an administrative user called 'postgres'.

`template1=# alter user postgres with encrypted password 'PASS';` [use your own password you will need it later for the configuration files.]

`template1=# \q` 

## Postgress authentication configuration

Configure the authentication method for postgres and all other users connecting locally
In `/etc/postgresql/12/main/pg_hba.conf` change "peer" to md5 for the administrative account and local unix domain socket

    # Database administrative login by Unix domain socket
    local   all             postgres                                md5
    
    # TYPE  DATABASE        USER            ADDRESS                 METHOD
    
    # "local" is for Unix domain socket connections only
    local   all             all                                     md5
    # IPv4 local connections:
    host    all             all             127.0.0.1/32            md5

Next, we want to only be able to connect to the database from the local machine

In `/etc/postgresql/12/main/postgresql.conf`

uncomment the line

`listen_addresses = 'localhost'`

Restart the postgres server

`sudo service postgresql restart`

Finally, log back in to postgres to create the database,

`sudo -u postgres psql`

`postgres=# create database seaice with owner postgres;`

`postgres-# \q`

clone the repository in the home directory

`git clone https://github.com/metadata-research/yamz.git`

`cd yamz`

The contents of the directory are:

| Filename         | Description                                                         |
| ---------------- | ------------------------------------------------------------------- |
| sea.py           | Console utility for scoring and classifying terms and other things. |
| ice.py           | Web server front end.                                               |
| digest.py        | Console email notification utility.                                 |
| requirements.txt | Python package dependencies.                                        |
| seaice/          | The SeaIce Python module.                                           |
| html/            | HTML templates, static Javascript and CSS, including bootstrap.js.  |
| doc/             | API documentation and tools for building it.                        |
| data/            | Data exported from live site.                                       |
| .seaice/         | DB credentials template                                             |
| .seaice_auth     | API keys, app key template file.                                    |

Create/edit the configuration file called `.seaice` for the database and user account you set up like the following but with the credentials you choose. There is a template in the repository, but the production passwords should obviously not be made public. This file is used by the SeaIce DB connector to grant access to the database.

    [default]
      dbname = seaice
      user = postgres
      password = PASS
    [contributor]
      dbname = seaice
      user = contributor
      password = PASS
    [reader]
      dbname = seaice
      user = reader
      password = PASS

Set permissions with

`chmod 600 .seaice`

## Python environment

Install the packagages listed in `requirements.txt`. You can use a Python virtual environment if you like. 

`pip install -r requirements.txt`

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

    Authorized redirect URI  . . . . . . http://localhost:5000/authorized
                                         http://localhost/authorized
                                         https://domain.name/authorized

The credentials minus the port is for when the proxy web server is set up and you are no longer using the flask development server and have set up https on a named server.

In each case, you should obtain a pair of values to put into another configuration file called '.seaice_auth'.  Create or edit this file,
replacing google_client_id with the returned 'Client ID' and replacing google_client_secret with the returned 'Client secret'. The app secret is for the flask application and just be a unique and random string. Here's one way to do it

 `python -c 'import os; print(os.urandom(16))'`

You can use a sepaprate set of credentials for the production instance if you like (as in the example below), just separate them with a label which you can pass when you initialize the database [dev] is the default specified in ice.py. 

Add additional credentials for other authentication services (right now the only other supported is ORCID)

    [dev]
     google_client_id = google_client_id_placeholder [these come from the google cloud api console]
     google_client_secret = google_client_secret_placeholder
     orcid_client_id = orcid_client_id_placehoder [these come from 'developer tools' under your profile in the ORCID portal]
     orcid_client_secret = orcid_client_secret_placeholder
     app_secret = SECRET
    [production] 
     google_client_id = google_client_id_placeholder
     google_client_secret = google_client_secret_placeholder
     app_secret = SECRET
     orcid_client_id = orcid_client_id_placehoder
     orcid_client_secret = orcid_client_secret_placeholder

Assign the appropriate permissions to the file

`chmod 600 .seaice_auth`

Initialize the DB schema and tables

`$ ./sea.py --init-db`

set up user standard read/write permissions on the table.

`sudo -u postgres psql`

`postgres=# \c seaice;`

`seaice=# create user contributor with encrypted password 'PASS';`

`seaice=# grant usage on schema SI, SI_Notify to contributor;`

`seaice=# grant select, insert, update, delete on all tables in schema SI, SI_Notify to contributor;`

`seaice=# \q`

## Testing

./ice.py

or

`export FLASK_APP=ice.py`

`export FLASK_ENV=development`

`flask run`

Adding terms won't work without a minter password, even on local dev version. Note also that minter password can't be set on local (doesn't do anything) and will currently only read from the heroku chunk in .seaice_auth
  
If all goes well, you should be able to navigate to your server by typing
'http://localhost:5000' in the address bar. To verify that you've set up
Google OAuth-2.0 correctly, try logging in. This will create an account.

Try adding a new term, modifying and deleting a term, and commenting on
terms. To classify a term, do:

  $ ./sea.py --config=.seaice --classify-terms

If you want test whether uWSGI can serve the application

`uwsgi --socket 0.0.0.0:5000 --protocol=http -w ice:app`

http://your_server_ip:5000

## Deploying to Production

Create a `yamz.ini` file in the yamz directory. There is a template in the repository

    [uwsgi]
    module = ice:app

    master = true
    processes = 5

    socket = yamz.sock
    chmod-socket = 660
    vacuum = true
    
    die-on-term = true

Create a unit file `yamz.service` within the `/etc/systemd/system` directory. There is a template in the repository. _usr1_ is a standin for the username that is associated with the running instance of your webserver.
  
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

Yamz (ice) is now running, waiting for requests on the socket file

## Configuring Nginx to Proxy Requests

Create a new server block configuration file in Nginx's sites-available directory.

For example ` sudo nano /etc/nginx/sites-available/yamz`

    server {
        listen 80;
        server_name yamz.link www.yamz.link;
        location / {
            include uwsgi_params;
            uwsgi_pass unix:/home/cr625/yamz/yamz.sock;
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

You no longer need the http entry exception in the firewall

`sudo ufw delete allow 'Nginx HTTP'`


## Scheduled tasks
## Mail notification

## Documentation

## Exporting the dictionary

The SeaIce API includes queries for importing and exporting database tables
in JSON formatted objects. This could be used to backup the entire database.
Note however that imports must be done in the proper order in order to satisfy
foreign key constraints.

For the time being, the most up to date version resides in heroku. This is already exported in the /json directory but if you need
to do it again, First install the heroku cli https://devcenter.heroku.com/articles/heroku-cli and login


`heroku config -a yamz | grep DATABASE_URL`
  
It is not necessary to enter a heroku shell to do this. If you have yamz set up in your test enviromenent, just
    
`export DATABASE_URL=<result>`
 
`./sea.py --config=heroku --export=Users >users.json`

`./sea.py --config=heroku --export=Terms >terms.json`

`./sea.py --config=heroku --export=Comments >comments.json`

`./sea.py --config=heroku --export=Tracking >tracking.json`

To reset the database, drop the table
  
`./sea.py --drop-db --init-db -q`

and import the json data in the following order:

`./sea.py --import=Users <json/users.json`

`./sea.py --import=Terms <json/terms.json`

`./sea.py --import=Comments <json/comments.json`

`./sea.py --import=Tracking <json/tracking.json`

