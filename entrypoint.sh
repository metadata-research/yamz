#!/bin/bash
set -e

# Start PostgreSQL in background
/etc/init.d/postgresql start

# Wait for it to come up
sleep 5

# Setup DB
sudo -u postgres psql --command "ALTER USER postgres WITH SUPERUSER PASSWORD 'PASS';"
sudo -u postgres createdb -O postgres yamz
sudo -u postgres psql yamz < /yamz/yamz.sql

# Run Flask app
exec python3 -m flask run -h 0.0.0.0 -p 5000
