
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

`sudo -u postgres psql template1`

Postgres psql requires an administrative user called 'postgres'.

`template1=# alter user postgres with encrypted password 'PASS';` [use your own password you will need it later for the configuration files.]

`template1=# \q` 

## Postgress authentication configuration
Configure the authentication method for postgres and all other users connecting locally
In `/etc/postgresql/12/main/pg_hba.conf` change "peer" to md5 for the administrative account and local unix domain socket

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

`postgres=# create user contributor with encrypted password 'PASS';`

clone the repository in the home directory from `https://github.com/cr625/yamz.git`

Change to the appropriate branch

`cd yamz`

`git checkout uwsgi_updates`

`cd uwsgi_updates`

| Filename         | Description                                                         |
| ---------------- | ------------------------------------------------------------------- |
| sea.py           | Console utility for scoring and classifying terms and other things. |
| ice.py           | Web server front end.                                               |
| digest.py        | Console email notification utility.                                 |
| requirements.txt | Python package dependencies.                                        |
|                  |                                                                     |
| seaice/          | The SeaIce Python module.                                           |
| html/            | HTML templates, static Javascript and CSS, including bootstrap.js.  |
| doc/             | API documentation and tools for building it.                        |
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

Initialize the DB schema and tables

`$ ./sea.py --init-db --config=.seaice`

set up user standard read/write permissions on the table 

`sudo -u postgres psql`

`postgres=# \c seaice;`

`postgres=# grant usage on schema SI, SI_Notify to contributor;`

`postgres=# grant select, insert, update, delete on all tables in schema SI, SI_Notify to contributor;`

`postgres=# \q`


## OAuth Credentials and appkey

YAMZ uses Google for third party authentication (OAuth-2.0) management of
logins. Visit https://console.cloud.google.com to set this service up
for your instance. Navigate to something like APIs and Services -> Credentials
and select whatever lets you create a new OAauth client ID.  For local
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
replacing google_client_id with the returned 'Client ID' and replacing google_client_secret with the returned 'Client secret'. The app secret is for the flask application and just be a unique and random string.

You can use a sepaprate set of credentials for the production instance if you like, just separate them with a label which you can pass when you initialize the database [dev] is the default specified in ice.py. The identifier API will not work with local host so to get things set up you might use the merged version as an intermediate setup.

    [dev]
     google_client_id = google_client_id_placeholder
     google_client_secret = google_client_secret_placeholder
     app_secret = SECRET
    [production] (if making a second set of credentials. Don't forget to pass the name of this section to ice.py when running the front end)
     google_client_id = google_client_id_placeholder
     google_client_secret = google_client_secret_placeholder
     app_secret = SECRET


Assign the appropriate permissions to the file

`chmod 600 .seaice_auth`

## Python environment
Install the packagages listed in `requirements.txt`. You can use a Python virtual environment if you like. It is a good
idea to install wheel with pip to ensure packages will install even if they are missing wheel archives.

`pip install wheel`
`pip install -r requirements.txt`


N2T persistent identifier resolver credentials
==================================================

Whenever a new term is created, YAMZ uses an API to n2t.net (maintained by
the California Digital Library) in order to generate ("mint") a persistent
identifier.  The main role of n2t.net is to be a resolver for the public-
facing URLs that persistently identify YAMZ terms.  It is necessary to
provide a minter password for API access to this web service.  To do so
include a line in ".seaice_auth" for every view:

   minter_password = PASS

A password found in the MINTER_PASSWORD environment variable, however, will
be preferred over the file setting.  This password is used again in the
API call to store metadata in a YAMZ binder on n2t.net.  The main bit of
metadata stored is the redirection target URL that supports resolution of
ARK identifiers for YAMZ terms.

Because real identifiers are meant to be persistent, no local or test
instance of YAMZ should ever set the boolean "prod_mode" parameter in
".seaice_auth".  For such instances the generated and updated terms
should just be for identifiers meant to be thrown away.  Only on the
real production instance of YAMZ, when you're done testing term creation
and update, should it be set to "enable" (the default is don't enable).



##Testing
Set the environment variable for flask
export FLASK_APP=ice.py

test whether uWSGI can serve the application

`uwsgi --socket 0.0.0.0:5000 --protocol=http -w ice:app`

http://your_server_ip:5000

    
Adding terms won't work without a minter password, even on local dev version. Note also that minter password can't be set on local (doesn't do anything) and will currently only read from the heroku chunk in .seaice_auth
  

If all goes well, you should be able to navigate to your server by typing
'http://localhost:5000' in the address bar. To verify that you've set up
Google OAuth-2.0 correctly, try logging in. This will create an account.

Try adding a new term, modifying and deleting a term, and commenting on
terms. To classify a term, do:

  $ ./sea.py --config=.seaice --classify-terms


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



Create a unit file `yamz.service` within the `/etc/systemd/system` directory. There is a template in the repository.
  
    [Unit]
    Description=uWSGI instance to serve yamz
    After=network.target
    
    [Service]
    User=usr1 [The unix user associated with the proxy server. See below.]
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

# Configuring Nginx to Proxy Requests
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

# Mailgun
YAMZ provides an email notification service for users who opt in. A utility
called 'digest' collects for each user all notifications that haven't
previously been emailed into a single digest. The code uses a heroku backend
app called Mailgun for SMTP service. To set this up, simply type (you may be
asked to verify your heroku account with a credit card, but note your card
should not be charged for the most basic service level)

  $ heroku addons:create mailgun

This sets a number of instance environment variables (see "heroku config").
Of them the code uses "MAILGUN_SMTP_LOGIN" and "MAILGUN_SMTP_PASSWORD" to
connect to Mailgun. Normally that happens when notifications are harvested
by the scheduler (below), but to send out notifications manually, type:

  $ heroku run python digest.py


2.3 Heroku-Scheduler

There are two periodic jobs that need to be scheduled in YAMZ: the term
classifier and the email digest. To set this up, do:

  $ heroku addons:create scheduler
  $ heroku addons:open scheduler

The second command will take you to the web interface for the scheduler. Add
the following two jobs:

  "python sea.py --classify-terms" . . . . . every 10 minutes
  "python digest.py" . . . . . . . . . . . . once per day


2.4 Starting the instance


Now that your instance is all prepared, you can get it up and running with

  $ git push heroku deploy_keys:master

This pushes the secret keys found in the local deploy_keys branch so that
they update the remote master branch on heroku.  (xxx see section 1.4 and
??? for setting the secrets)
# xxx app_secret is the (api key?) password from netrc, or "heroku auth:token"?


2.5 Making changes


Deploying changes to heroku is made easy with Git. Suppose we have changes
to 'master' that we want to push to heroku.

  $ git checkout deploy_keys
  $ git merge master          # updates deploy_keys with latest master commits
  $ git push heroku deploy_keys:master

The first command checks out the already created local 'deploy_keys' branch.
The second command merges the latest commits from the master branch into it,
and the final command updates the heroku master branch, which also restarts
the instance.  This keeps the secrets outside the master branch.

When you next checkout the master branch, however, your keys and secrets in
the .seaice* files will be overwritten, so you may want to save them in
separate files that you can copy back in to the branch when you later deploy
again; just make sure those separate files don't ever become part of any
branch that will show up in the public github repo.


2.6 Exporting the dictionary

The SeaIce API includes queries for importing and exporting database tables
in JSON formatted objects. This could be used to backup the entire database.
Note however that imports must be done in the proper order in order to satisfy
foreign key constraints. To back up the dictionary, do:

  $ heroku config | grep DATABASE_URL
  DATABASE_URL: <whatever>
  $ export DATABASE_URL=<whatever>
  $ ./sea.py --config=heroku --export=Terms >terms.json


3. URL forwarding


The current stable implementation of YAMZ is redirected from http://yamz.net.
Setting this up takes a bit of doing. The following instructions are synthsized
from http://lifesforlearning.com/heroku-with-godaddy/ for redirecting a domain
name managed by GoDaddy to a Heroku app.

Launch the "Domains" app on GoDaddy. Under "Forward Domain" for the appropriate
domain (let's call it "fella.org"), add the following settings:

 Forward to . . . . . . . . . . . . . . . . . . . . http://www.fella.org
 Redirect type  . . . . . . . . . . . . . . . . . . 301 (Permanent)
 Forward settings . . . . . . . . . . . . . . . . . Forward only
 Update nameservers and DNS settings
           to support this change . . . . . . . . . yes

Next, under "Manage DNS", remove all entries except for 'A (Host)' and 'NS
(Nameserver)', and add the following under 'CName (Alias)':

 Record type  . . . . . . . . . . . . . . . . . CNAME (Alias)
 Host . . . . . . . . . . . . . . . . . . . . . www
 Points to  . . . . . . . . . . . . . . . . . . http://fella.herokuapp.com
 TTL  . . . . . . . . . . . . . . . . . . . . . 1 Hour

Next, change the IP address for entry '@' under 'A (Host)' to 50.63.202.31
(the current IP address of yamz.net).

That's it for DNS configuration. The last thing we need to do is modify the
redirect URLs in the Google OAuth API. Edit the authorized javascript origins
and redirect URI by replacing "fella.herokuapp.com" with "fella.org" and
save.

It can take a couple hours to a day for your DNS settings to propogate. Once
it's done, you can navigate to YAMZ by typing "fella.org" into your browser.
Try logging in to verify that the OAuth settings are also correct.


4. Building the docs

The seaice package (but not this README file) is autodoc'ed using
python-sphinx. To install on Ubuntu:

  $ sudo apt-get install python-sphinx

The directory doc/sphinx includes a Makefile for exporting the docs to
various media. For example,

  make html
  make latex
