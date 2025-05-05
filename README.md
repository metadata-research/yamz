
# YAMZ Metadictionary

This is the README for the YAMZ vocabulary builder for data and metadata.
It includes instructions for deploying on a local machine for testing and on
a Linux-based environment for a scalable production version.

The application requires PostgreSQL to support full-text search. 

The following is an example configuration. You can substitute your own database names and users.

For a comprehensive setup guide covering Windows, Ubuntu, and macOS, please refer to [SETUP.md](SETUP.md).

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

(macOS) `brew services restart postgresql`

Finally, log back in to postgres to create the database,

Add a db password for the user 'postgres'. 
   
    `sudo -u postgres psql template1`
    `postgres=# alter user postgres with encrypted password 'PASS';`

The database name is yamz by default. In the shared yamz dev and prd
servers the name is yamz_dev and yamz_prd, respectively.

`sudo -u postgres psql`

`postgres=# create database yamz with owner postgres;`

`postgres-# \q`

On macOS, usually one time:

    createuser -d postgres
    psql -U postgres -c "alter user postgres with encrypted password 'PASS'"

On macOS, every so often you need to recreate the database:

    psql -U postgres -c 'create database yamz with owner postgres'

On macOS, regularly need to restart server:

    brew services restart postgresql

4. Placeholder

5. Clone the repository

    `git clone https://github.com/metadata-research/yamz.git`

6. switch to the yamz directory

    `cd yamz`

7. Create a python 3 virtual environment

    `virtualenv env`

On macOS, you may have to first install python3 and virtualenv (https://gist.github.com/pandafulmanda/730a9355e088a9970b18275cb9eadef3)

    brew install python3
    # failing on mac, use python3 -m venv env
    #  brew install pipx ?
    pip3 install virtualenv
    virtualenv env

8. Activate the virtual environment:

    `source env/bin/activate`

9.  Install the Python dependencies:

    `pip install -r requirements.txt`


10. Copy the `\_config.py` file in the root directory to `config.py` (remove the leading underscore). Modify the new file with the appropriate credentials. `config.py` is included in `.gitignore` so the modified file should not be pushed to the repository.

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

Note: The `contributor` user mentioned in the database URI is a custom PostgreSQL database user you'll need to create. You can replace it with any username you prefer, but make sure to create this user in PostgreSQL with appropriate permissions.

11. Set the `FLASK_APP` variable:

    `export FLASK_APP=yamz.py`

12. On the first run, create the db:

    `flask db init`

On subsequent runs:

    flask db migrate
    flask db upgrade     

XXX how does a new user set up some data to demo the system with?

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

To import existing data to a new instance of YAMZ, please follow the instructions in the [Database Backup and Restoration](#backups) section below. This is the recommended approach rather than running individual import scripts.

## OAuth Credentials and appkey

YAMZ uses Google for third party authentication (OAuth-2.0) management of
logins. Visit https://console.cloud.google.com to set this service up
for your instance. Navigate to something like APIs and Services -> Credentials
and select whatever lets you create a new OAuth client ID.  For local
configuration, supply these answers:

    Application type . . . . . . . . . . Web application

    Authorized javascript origins  . . . http://localhost:5000
                                         http://localhost:5001
                                         https://localhost
                                         https://yourdomain.com

    Authorized redirect URI  . . . . . . http://localhost:5000/g_authorized
                                         http://localhost:5001/g_authorized
                                         https://localhost/g_authorized
                                         https://yourdomain.com/g_authorized

Note: For production deployments, you must use HTTPS URLs. For local development, HTTP works but requires specifying the port.

The credentials without the port are for when a proxy web server is set up, you are no longer using the Flask 
development server, and have set up HTTPS on a named server. You can also serve the application locally using 
HTTPS by invoking uWSGI with the appropriate ini file from within the yamz directory: `uwsgi yamz_local.ini`. This method requires generating an SSL certificate for localhost and adding it to your browser or OS certificate store.

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

Create a unit file `yamz.service` within the `/etc/systemd/system` directory. _usr1_ is a placeholder - you should replace it with an actual system user that you've created to run the web server application.
  
    [Unit]
    Description=uWSGI instance to serve yamz
    After=network.target
    
    [Service]
    User=your_username  # Replace with an actual system user you've created
    Group=www-data
    WorkingDirectory=/home/your_username/yamz  # Replace with actual user's home directory
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
        server_name yamz.net www.yamz.net;
        location / {
w:510-642-3279
            include uwsgi_params;
            uwsgi_pass unix:/home/your_username/yamz/yamz.sock;  # Replace with your actual username path
        }
    }


Save and close the file when you are finished.

To enable the Nginx server block configuration, link the file to the sites-enabled directory:

`sudo ln -s /etc/nginx/sites-available/yamz /etc/nginx/sites-enabled`


Remove the default site or it will block the proxying.

`sudo unlink /etc/nginx/sites-enabled/default`

Test for syntax errors.

`sudo nginx -t`

The YAMZ prototype is currently hosted at http://yamz.net

Note: If you are installing your own instance of YAMZ, you should replace all references to "yamz.net" with your own domain name throughout this setup process.

Make sure the user in the /etc/nginx/nginx.conf file is the user you want to run the project under

Restart nginx.

`sudo systemctl restart nginx`

## Secure the Application

You can do this anyway you like, but currently it is with Certbot and its Nginx plugin

The Nginx plugin will take configure Nginx and reload the config when necessary. To use it

`sudo certbot --nginx -d yamz.net -d www.yamz.net`

Make sure there is a generic type a record and one for www for your domain.

Certbot will ask you whether you wish to redirect all http traffic to https (removing http access).

## Backups

Backup on production
`pg_dump -C -Fp -f yamz.sql -U postgres yamz`

This will create a yamz.sql file that is portable.

For example, to restore on your laptop from a given daily backup:

    service yamz stop
    dropdb -U postgres yamz
    psql -U postgres -f yamz_2023-05-11.sql

    dropdb -U postgres yamz_prd
    psql -U postgres -f yamz_2025-04-02.sql

The database name is yamz by default. In the shared yamz dev and prd
servers the name is yamz_dev and yamz_prd, respectively.
To update the yamz_dev database from current production database:

    service yamz stop
    psql -U postgres
    postgres=# CREATE DATABASE yamz_dev WITH TEMPLATE yamz

## Development Environment
The development environment for YAMZ should be set up as follows:

1. Use the `dev` branch for development work
2. Set up a separate database (e.g., `yamz_dev`) to avoid affecting production data
3. For local development, use the Flask development server with:
   ```bash
   export FLASK_APP=yamz.py
   export FLASK_ENV=development
   export FLASK_RUN_PORT=5001
   flask run
   ```

4. When testing with uWSGI:
   - Use a different socket file name (e.g., `yamz_dev.sock` instead of `yamz.sock`)
   - Create a separate service configuration file (e.g., `yamz_dev.service`)
   - Point the database URI to your development database

### Database Environments

YAMZ uses two separate databases to maintain isolation between development and production environments:

#### Production Database (`yamz` or `yamz_prd`)
- Contains the live, publicly accessible data
- Should only be modified through the production application
- Used by the main application instance at yamz.link
- Any changes directly affect end users
- Backed up regularly to prevent data loss

#### Development Database (`yamz_dev`)
- Used for testing new features and changes without affecting production data
- Can be reset or modified without impacting end users
- Used by the development instance at yamz-dev.yamz.link
- Can be periodically refreshed from a production backup to stay current
- Ideal for running migrations and schema changes before applying to production

When working on the application, always ensure your config.py is pointing to the appropriate database for your current task. For local development and testing, using the development database or an entirely separate local database is strongly recommended.

For testing that doesn't require a full PostgreSQL database, the application includes a SQLite-based test suite that can be run without any additional setup.

For more details on setting up a proper development environment, see the [SETUP.md](SETUP.md) file.

## Contributing to YAMZ

We welcome contributions to the YAMZ project! This section outlines the process for making changes and submitting them for review.

### Setting Up Your Development Environment

1. **Fork the Repository**
   - Visit the [YAMZ GitHub repository](https://github.com/metadata-research/yamz)
   - Click the "Fork" button in the top right to create your own copy

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/YOUR-USERNAME/yamz.git
   cd yamz
   ```

3. **Add the Upstream Repository**
   ```bash
   git remote add upstream https://github.com/metadata-research/yamz.git
   ```

4. **Create a Development Database**
   ```bash
   # Create a separate database for development
   psql -U postgres -c "CREATE DATABASE yamz_dev;"
   
   # If you want to populate it with production data:
   pg_restore -U postgres -d yamz_dev yamz_prd_backup.dump
   ```

5. **Configure Your Local Environment**
   - Copy `_config.py` to `config.py` and set the database URI to point to `yamz_dev`
   ```python
   SQLALCHEMY_DATABASE_URI = "postgresql://postgres:your_password@localhost/yamz_dev"
   ```

### Making Changes

1. **Create a Feature Branch**
   - Always create a new branch for your changes based on the latest dev branch
   ```bash
   # Ensure your fork is up to date
   git fetch upstream
   git checkout dev
   git merge upstream/dev
   
   # Create a new branch with a descriptive name
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write your code, fix bugs, or add new features
   - Follow the existing code style and conventions
   - Add or update tests as necessary

3. **Test Your Changes**
   - Run the application locally to test your changes
   - Ensure all existing functionality still works
   - Fix any issues that arise during testing

4. **Commit Your Changes**
   - Make focused, logical commits with clear messages
   ```bash
   git add .
   git commit -m "Brief description of your changes"
   ```

### Submitting Your Changes

1. **Push Your Branch**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request**
   - Go to your fork on GitHub
   - Click "Pull Request" button
   - Select your feature branch as the source
   - Select the `dev` branch of the metadata-research/yamz repository as the target
   - Provide a clear title and description of your changes
   - Submit the pull request

3. **Code Review Process**
   - Maintainers will review your pull request
   - Address any feedback or requested changes
   - Once approved, your changes will be merged into the dev branch

### Best Practices

- **Keep Pull Requests Focused**: Each PR should address a single concern or feature
- **Update Regularly**: Keep your fork and branches updated with the latest changes from upstream
- **Document Your Code**: Add comments and update documentation as needed
- **Follow Coding Standards**: Maintain consistent style with the existing codebase
- **Test Thoroughly**: Ensure your changes don't break existing functionality

### Common Issues and Solutions

For help with common development issues, see the "Common Development Issues" section in [SETUP.md](SETUP.md).


## Reinstalling YAMZ Environment

1. Backup your configuration and database:
   ```bash
   # Save your config.py
   cp config.py ~/config.py.backup
   
   # Backup your database (Ubuntu example)
   sudo -u postgres pg_dump -C -Fp -f yamz.sql yamz
   ```

2. Drop and recreate the database:
   ```bash
   sudo -u postgres psql
   postgres=# DROP DATABASE yamz;
   postgres=# CREATE DATABASE yamz;
   postgres=# \q
   ```

3. Set up a fresh installation:
   ```bash
   # Clone the repository
   git clone https://github.com/metadata-research/yamz.git
   cd yamz
   git checkout dev
   
   # Restore your config file
   cp ~/config.py.backup config.py
   
   # Create and activate virtual environment
   python3 -m venv env
   source env/bin/activate
   pip install -r requirements.txt
   
   # Restore your database
   sudo -u postgres psql -f yamz.sql
   ```

4. If you want to use migrations with a restored database:
   ```bash
   # Clear existing alembic version
   sudo -u postgres psql yamz -c "DELETE FROM alembic_version;"
   
   # Initialize migrations
   export FLASK_APP=yamz.py
   flask db init
   ```

For more detailed restoration instructions, refer to the [SETUP.md](SETUP.md) file.
