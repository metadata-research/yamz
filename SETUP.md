# YAMZ Metadictionary: Comprehensive Setup Guide

This guide provides detailed instructions for setting up YAMZ on different operating systems (Windows, Ubuntu, and macOS) for both development and production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
  - [Windows](#windows-prerequisites)
  - [Ubuntu](#ubuntu-prerequisites)
  - [macOS](#macos-prerequisites)
- [PostgreSQL Setup](#postgresql-setup)
  - [Windows](#windows-postgresql)
  - [Ubuntu](#ubuntu-postgresql)
  - [macOS](#macos-postgresql)
- [Application Setup](#application-setup)
  - [Clone Repository](#clone-repository)
  - [Python Environment](#python-environment)
  - [Application Configuration](#application-configuration)
- [Database Configuration](#database-configuration)
  - [Creating the Database](#creating-the-database)
  - [Running Migrations](#running-migrations)
  - [Restoring from Backup](#restoring-from-backup)
- [OAuth Configuration](#oauth-configuration)
  - [Google OAuth](#google-oauth)
  - [ORCID OAuth](#orcid-oauth)
- [Running the Application](#running-the-application)
  - [Development Mode](#development-mode)
  - [Production Deployment](#production-deployment)
- [Database Backup and Restoration](#database-backup-and-restoration)
  - [Creating Backups](#creating-backups)
  - [Restoring Backups](#restoring-backups)
  - [Transferring Backups Between Environments](#transferring-backups-between-environments)
- [Troubleshooting](#troubleshooting)
  - [Database Issues](#database-issues)
  - [OAuth Issues](#oauth-issues)
  - [Application Issues](#application-issues)
  - [Deployment Issues](#deployment-issues)

## Prerequisites

### Windows Prerequisites

1. **PostgreSQL**:
   - Download and install PostgreSQL from the [official website](https://www.postgresql.org/download/windows/)
   - Recommended version: 13.x or later
   - During installation, remember the password you set for the postgres user

2. **Python**:
   - Download and install Python 3.9+ from the [official website](https://www.python.org/downloads/windows/)
   - Ensure "Add Python to PATH" is checked during installation

3. **Git**:
   - Download and install Git from the [official website](https://git-scm.com/download/win)

4. **Visual C++ Build Tools** (required for some Python packages):
   - Download and install from [Microsoft's website](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

### Ubuntu Prerequisites

1. **PostgreSQL**:
   ```bash
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   ```

2. **Python**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   ```

3. **Git**:
   ```bash
   sudo apt update
   sudo apt install git
   ```

4. **Development Tools**:
   ```bash
   sudo apt install build-essential libpq-dev
   ```

### macOS Prerequisites

1. **Homebrew** (package manager):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **PostgreSQL**:
   ```bash
   brew install postgresql
   ```

3. **Python**:
   ```bash
   brew install python3
   ```

4. **Git**:
   ```bash
   brew install git
   ```

## PostgreSQL Setup

### Windows PostgreSQL

1. **Start PostgreSQL Service**:
   - The service should start automatically after installation
   - You can check in Services (services.msc) to ensure "postgresql-x64-XX" is running

2. **Configure PostgreSQL**:
   - Open pgAdmin (installed with PostgreSQL)
   - Connect to the server using the password you set during installation
   - Right-click on "Login/Group Roles" and create a new role if needed
   - Right-click on "Databases" to create a new database for YAMZ

3. **Configure Authentication**:
   - Open the directory where PostgreSQL is installed (typically `C:\Program Files\PostgreSQL\XX\data`)
   - Edit `pg_hba.conf` to change authentication method from `scram-sha-256` to `md5` for local connections:
     ```
     # TYPE  DATABASE        USER            ADDRESS                 METHOD
     host    all             all             127.0.0.1/32            md5
     host    all             all             ::1/128                 md5
     ```

4. **Restart PostgreSQL Service**:
   - Open Services
   - Find the PostgreSQL service and restart it

### Ubuntu PostgreSQL

1. **Configure PostgreSQL Authentication**:
   ```bash
   sudo -u postgres psql
   postgres=# ALTER USER postgres WITH PASSWORD 'your_password';
   postgres=# \q
   ```

2. **Edit PostgreSQL Configuration**:
   ```bash
   sudo nano /etc/postgresql/[version]/main/pg_hba.conf
   ```
   
   Change authentication method from `peer` to `md5` for local connections:
   ```
   # TYPE  DATABASE        USER            ADDRESS                 METHOD
   local   all             all                                     md5
   # IPv4 local connections:
   host    all             all             127.0.0.1/32            md5
   ```

3. **Configure PostgreSQL Network Settings**:
   ```bash
   sudo nano /etc/postgresql/[version]/main/postgresql.conf
   ```
   
   Uncomment and modify:
   ```
   listen_addresses = 'localhost'
   ```

4. **Restart PostgreSQL**:
   ```bash
   sudo service postgresql restart
   ```

### macOS PostgreSQL

1. **Start PostgreSQL Service**:
   ```bash
   brew services start postgresql
   ```

2. **Configure PostgreSQL**:
   ```bash
   psql postgres
   postgres=# CREATE ROLE postgres WITH LOGIN SUPERUSER;
   postgres=# ALTER USER postgres WITH PASSWORD 'your_password';
   postgres=# \q
   ```

3. **Verify Service is Running**:
   ```bash
   brew services list
   ```

## Application Setup

### Clone Repository

On all platforms:

```bash
git clone https://github.com/metadata-research/yamz.git
cd yamz
git checkout dev
```

### Python Environment

#### Windows

```bash
python -m venv env
.\env\Scripts\activate
pip install -r requirements.txt
```

#### Ubuntu/macOS

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### Application Configuration

1. **Create Configuration File**:
   - Copy `_config.py` to `config.py`
   - Edit `config.py` with your database and OAuth credentials

   ```python
   # Example config.py
   import os
   
   class Config(object):
       SECRET_KEY = os.environ.get("SECRET_KEY") or "your-secret-key"
       
       # database
       SQLALCHEMY_DATABASE_URI = "postgresql://postgres:your_password@localhost/yamz"
       # Note: You can also create a custom database user instead of using 'postgres'
       # SQLALCHEMY_DATABASE_URI = "postgresql://custom_username:your_password@localhost/yamz"
       SQLALCHEMY_TRACK_MODIFICATIONS = False
       
       # oauth
       OAUTH_CREDENTIALS = {
           "google": {
               "id": "your-google-client-id",
               "secret": "your-google-client-secret",
           },
           "orcid": {
               "id": "your-orcid-client-id",
               "secret": "your-orcid-client-secret",
           },
       }
       
       # Rest of the configuration...
   ```

## Database Configuration

### Creating the Database

#### Windows

Through pgAdmin:
- Connect to your PostgreSQL server
- Right-click on "Databases" and select "Create" → "Database"
- Name it "yamz" and set owner to "postgres"

Or through command line:
```bash
psql -U postgres
postgres=# CREATE DATABASE yamz WITH OWNER postgres;
postgres=# \q
```

#### Ubuntu

```bash
sudo -u postgres psql
postgres=# CREATE DATABASE yamz WITH OWNER postgres;
postgres=# \q
```

#### macOS

```bash
psql postgres -U postgres
postgres=# CREATE DATABASE yamz WITH OWNER postgres;
postgres=# \q
```

### Running Migrations

After setting up the database and configuring the application:

```bash
# Set Flask app environment variable
# Windows
set FLASK_APP=yamz.py

# Ubuntu/macOS
export FLASK_APP=yamz.py

# Initialize database (first run only)
flask db init

# For subsequent runs or after schema changes
flask db migrate
flask db upgrade
```

### Restoring from Backup

If you have a database backup file, you can restore it instead of running migrations:

#### Windows

```bash
# Restore from a SQL file
psql -U postgres -f yamz.sql

# Or restore from a custom format backup
pg_restore -U postgres -d yamz yamz_prd_backup.dump
```

#### Ubuntu

```bash
# Restore from a SQL file
sudo -u postgres psql -f yamz.sql

# Or restore from a custom format backup
sudo -u postgres pg_restore -d yamz yamz_prd_backup.dump
```

#### macOS

```bash
# Restore from a SQL file
psql -U postgres -f yamz.sql

# Or restore from a custom format backup
pg_restore -U postgres -d yamz yamz_prd_backup.dump
```

## OAuth Configuration

### Google OAuth

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" → "Credentials"
4. Click "Create Credentials" → "OAuth client ID"
5. Select "Web application" as the application type
6. Add authorized JavaScript origins:
   - For local development: `http://localhost:5000` and `http://localhost:5001`
   - For production: your domain (e.g., `https://yamz.link`)
7. Add authorized redirect URIs:
   - For local development: `http://localhost:5000/g_authorized` and `http://localhost:5001/g_authorized`
   - For production: your domain redirect URI (e.g., `https://yamz.link/g_authorized`)
8. Copy the client ID and client secret to your `config.py` file

Note: For production, you'll need to use HTTPS URLs. For local development, Google requires port specification.

### ORCID OAuth

1. Go to the [ORCID Developer Tools](https://orcid.org/developer-tools)
2. Register a new application
3. Set the redirect URI:
   - For local development: `http://localhost:5000/orcid_authorized` or `http://localhost:5001/orcid_authorized`
   - For production: your domain redirect URI (e.g., `https://yamz.link/orcid_authorized`)
4. Copy the client ID and client secret to your `config.py` file

## Running the Application

### Development Mode

#### Windows

```bash
set FLASK_APP=yamz.py
set FLASK_ENV=development
set FLASK_RUN_PORT=5001
flask run
```

#### Ubuntu/macOS

```bash
export FLASK_APP=yamz.py
export FLASK_ENV=development
export FLASK_RUN_PORT=5001
flask run
```

The application will be available at `http://localhost:5001`

### Production Deployment

#### Prerequisites

For a production deployment, you'll need:

- A Linux server (Ubuntu recommended)
- Nginx as the reverse proxy
- uWSGI as the application server
- HTTPS certificates (Let's Encrypt recommended)

#### Setup Steps

1. **Create uWSGI Configuration**
   
   Create a `yamz.ini` file in the yamz directory:
   
   ```ini
   [uwsgi]
   module = yamz:app
   
   master = true
   processes = 5
   
   socket = yamz.sock
   chmod-socket = 660
   vacuum = true
   
   die-on-term = true
   ```

2. **Create Systemd Service**
   
   Create a file at `/etc/systemd/system/yamz.service`:
   
   ```ini
   [Unit]
   Description=uWSGI instance to serve yamz
   After=network.target
   
   [Service]
   User=your_username  # Replace with an actual system user you've created
   Group=www-data
   WorkingDirectory=/path/to/yamz  # Replace with actual path to your installation
   Environment="PATH=/path/to/yamz/env/bin"  # Replace with actual path
   ExecStart=/path/to/yamz/env/bin/uwsgi --ini yamz.ini  # Replace with actual path
   
   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and Start Service**
   
   ```bash
   sudo systemctl start yamz
   sudo systemctl enable yamz
   ```

4. **Configure Nginx**
   
   Create a file at `/etc/nginx/sites-available/yamz`:
   
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
   
       location / {
           include uwsgi_params;
           uwsgi_pass unix:/path/to/yamz/yamz.sock;
       }
   }
   ```
   
   Create a symbolic link:
   
   ```bash
   sudo ln -s /etc/nginx/sites-available/yamz /etc/nginx/sites-enabled
   ```

5. **Enable HTTPS with Certbot**
   
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

6. **Restart Nginx**
   
   ```bash
   sudo systemctl restart nginx
   ```

## Database Backup and Restoration

### Creating Backups

#### Plain SQL Format

```bash
# Windows
pg_dump -U postgres -C -Fp -f yamz.sql yamz

# Ubuntu
sudo -u postgres pg_dump -C -Fp -f yamz.sql yamz

# macOS
pg_dump -U postgres -C -Fp -f yamz.sql yamz
```

#### Custom Format (Compressed)

```bash
# Windows
pg_dump -U postgres -Fc -b -v -f yamz_backup.dump yamz

# Ubuntu
sudo -u postgres pg_dump -Fc -b -v -f yamz_backup.dump yamz

# macOS
pg_dump -U postgres -Fc -b -v -f yamz_backup.dump yamz
```

### Restoring Backups

#### From Plain SQL Format

```bash
# Windows
psql -U postgres -f yamz.sql

# Ubuntu
sudo -u postgres psql -f yamz.sql

# macOS
psql -U postgres -f yamz.sql
```

#### From Custom Format

```bash
# Windows
# First, drop the existing database if it exists
psql -U postgres -c "DROP DATABASE IF EXISTS yamz;"
psql -U postgres -c "CREATE DATABASE yamz;"
pg_restore -U postgres -d yamz yamz_backup.dump

# Ubuntu
sudo -u postgres psql -c "DROP DATABASE IF EXISTS yamz;"
sudo -u postgres psql -c "CREATE DATABASE yamz;"
sudo -u postgres pg_restore -d yamz yamz_backup.dump

# macOS
psql -U postgres -c "DROP DATABASE IF EXISTS yamz;"
psql -U postgres -c "CREATE DATABASE yamz;"
pg_restore -U postgres -d yamz yamz_backup.dump
```

### Transferring Backups Between Environments

#### From Production to Development

1. Create a backup of the production database:
   ```bash
   pg_dump -U postgres -Fc -b -v -f yamz_prod_backup.dump yamz
   ```

2. Transfer the file to your development machine (using SCP, SFTP, etc.):
   ```bash
   scp username@production-server:/path/to/yamz_prod_backup.dump /local/path/
   ```

3. Restore to your development database:
   ```bash
   # First, drop the existing database if it exists and create a new one
   psql -U postgres -c "DROP DATABASE IF EXISTS yamz_dev;"
   psql -U postgres -c "CREATE DATABASE yamz_dev;"
   
   # Then restore from the backup
   pg_restore -U postgres -d yamz_dev yamz_prod_backup.dump
   ```

### Common Development Issues

1. **Template Rendering Errors**: If you encounter "NoneType is not subscriptable" errors:
   - Check Jinja2 templates for proper handling of None values
   - Wrap operations on potentially None values in conditional checks
   - Example fix for handling None definitions in templates:
     ```jinja
     {% if term.definition %}
         {{ term.definition[0:200] }}
     {% else %}
         <em>No definition provided</em>
     {% endif %}
     ```

2. **Configuration File Syntax**: Ensure proper syntax in config.py:
   - Dictionary items should be separated by commas
   - Example:
     ```python
     OAUTH_CREDENTIALS = {
         "google": {
             "id": "your-google-client-id",
             "secret": "your-google-client-secret"
         },
         "orcid": {
             "id": "your-orcid-client-id",
             "secret": "your-orcid-client-secret"
         }
     }
     ```

## Troubleshooting

### Database Issues

#### Connection Refused

**Symptoms:**
- Error message: "could not connect to server: Connection refused"

**Solutions:**
1. **Check PostgreSQL Service:**
   ```bash
   # Windows: Check in services.msc
   # Ubuntu
   sudo service postgresql status
   # macOS
   brew services list
   ```
   
2. **Verify PostgreSQL Configuration:**
   - Ensure `postgresql.conf` has `listen_addresses = 'localhost'`
   - Restart PostgreSQL service after changes

3. **Check Connection Parameters:**
   - Verify username, password, host, and database name in your connection string
   - Test connection manually:
     ```bash
     psql -U postgres -h localhost yamz
     ```

#### Authentication Failed

**Symptoms:**
- Error message: "password authentication failed for user"

**Solutions:**
1. **Reset PostgreSQL Password:**
   ```bash
   # Ubuntu
   sudo -u postgres psql
   postgres=# ALTER USER postgres WITH PASSWORD 'new_password';
   # macOS/Windows
   psql -U postgres
   postgres=# ALTER USER postgres WITH PASSWORD 'new_password';
   ```

2. **Check pg_hba.conf:**
   - Ensure authentication method is set to `md5` for local connections
   - Restart PostgreSQL after changes

#### Database Migration Errors

**Symptoms:**
- Error during `flask db migrate` or `flask db upgrade`

**Solutions:**
1. **Reset Migration:**
   ```bash
   # Delete migrations folder
   rm -rf migrations
   # Reinitialize
   flask db init
   flask db migrate
   flask db upgrade
   ```

2. **Check Alembic Version in Database:**
   ```bash
   psql -U postgres yamz -c "SELECT * FROM alembic_version;"
   # If conflicts exist, consider:
   psql -U postgres yamz -c "DELETE FROM alembic_version;"
   ```

### OAuth Issues

#### Authentication Redirect Errors

**Symptoms:**
- Unable to authenticate with Google or ORCID
- Redirect errors after authentication attempt

**Solutions:**
1. **Verify Redirect URIs:**
   - Ensure redirect URIs in Google/ORCID developer console exactly match your application URLs
   - Include port number for development (e.g., `http://localhost:5001/g_authorized`)

2. **Check Credentials:**
   - Verify client ID and secret in `config.py` match those in the developer console

3. **HTTPS Requirements:**
   - For production, ensure your site uses HTTPS
   - For local development with Google, you may need to create a local certificate

#### Callback URL Not Working

**Symptoms:**
- After OAuth authorization, the callback URL fails

**Solutions:**
1. **Check URL Configuration:**
   - Ensure your application is running on the expected port
   - Verify that your OAuth provider has the correct callback URLs registered

2. **Browser Console Errors:**
   - Check browser console for JavaScript errors
   - Look for CORS issues or blocked redirects

### Application Issues

#### Missing Dependencies

**Symptoms:**
- Import errors when starting the application
- ModuleNotFoundError exceptions

**Solutions:**
1. **Verify Virtual Environment:**
   ```bash
   # Activate the virtual environment
   # Windows
   .\env\Scripts\activate
   # Ubuntu/macOS
   source env/bin/activate
   
   # Install requirements again
   pip install -r requirements.txt
   ```

2. **Check System Dependencies:**
   - Some packages require additional system libraries
   - On Ubuntu:
     ```bash
     sudo apt install libpq-dev python3-dev
     ```

#### Flask Application Not Found

**Symptoms:**
- "Error: Could not locate a Flask application"

**Solutions:**
1. **Set Environment Variable:**
   ```bash
   # Windows
   set FLASK_APP=yamz.py
   # Ubuntu/macOS
   export FLASK_APP=yamz.py
   ```

2. **Check File Location:**
   - Ensure you're in the correct directory
   - Verify `yamz.py` exists

#### Port Already in Use

**Symptoms:**
- "Error: Address already in use" when starting Flask

**Solutions:**
1. **Change Port:**
   ```bash
   # Windows
   set FLASK_RUN_PORT=5001
   # Ubuntu/macOS
   export FLASK_RUN_PORT=5001
   ```

2. **Find and Kill Process:**
   ```bash
   # Find process using port 5000
   # Windows
   netstat -ano | findstr :5000
   # Ubuntu/macOS
   lsof -i :5000
   
   # Kill the process
   # Windows
   taskkill /PID <pid> /F
   # Ubuntu/macOS
   kill -9 <pid>
   ```

### Deployment Issues

#### uWSGI Socket Permission Issues

**Symptoms:**
- "unable to connect to socket" in Nginx error logs

**Solutions:**
1. **Check Socket Permissions:**
   ```bash
   ls -la /path/to/yamz/yamz.sock
   ```

2. **Update Service Configuration:**
   - Ensure the socket is owned by the correct user and group
   - Modify the uWSGI configuration:
     ```ini
     chmod-socket = 660
     ```

3. **Check User and Group:**
   - Ensure the user running uWSGI is in the same group as Nginx (typically `www-data`)

#### Nginx Configuration Issues

**Symptoms:**
- 502 Bad Gateway or 504 Gateway Timeout errors

**Solutions:**
1. **Check Nginx Error Logs:**
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

2. **Verify uWSGI is Running:**
   ```bash
   sudo systemctl status yamz
   ```

3. **Test uWSGI Directly:**
   ```bash
   uwsgi --http :8000 --module yamz:app
   ```

#### SSL Certificate Issues

**Symptoms:**
- Browser warnings about insecure certificates
- Certificate errors in Nginx logs

**Solutions:**
1. **Renew Let's Encrypt Certificates:**
   ```bash
   sudo certbot renew
   ```

2. **Check Certificate Path:**
   - Verify the certificate paths in your Nginx configuration
   - Ensure certificates are readable by Nginx

3. **Test SSL Configuration:**
   ```bash
   sudo nginx -t
