
# YAMZ Metadata Dictionary

This is the README for the YAMZ metadictionary and includes instructions for
deploying on a local machine for testing and on a Linux based environment for a
scalable production version. These assume a Ubuntu GNU/Linux environment, but
should be easily adaptable to any system; YAMZ is written in Python and uses
only cross-platform packages.

The current application requires the use of a postgres database to support full text search. 

The following is an example configuration. You can substitute your own db names and users


1. Install postgres. Installation instructions may vary depending on the platform.

[postgres downloads](https://www.postgresql.org/download/)


2. Create a database in psql

[create database doc](https://www.postgresql.org/docs/current/sql-createdatabase.html)

(the installation should create a unix user postgres so something like sudo -u postgres psql)

postgres=# CREATE DATABASE yamz;

3. Create a postgres user. You can name it anything you like.

postgres=# CREATE USER contributor WITH ENCRYPTED PASSWORD 'PASS';


4. Grant priveleges to that user

postgres=# grant all privileges on database <dbname> to <username> ;


5. Switch to that db

postgres=# \c yamz;


4. Create a user/role

[create user/role doc](https://www.postgresql.org/docs/current/sql-createuser.html)




5. Clone the repository

git clone https://github.com/metadata-research/yamz.git

6. switch to the yamz directory

cd yamz

7. Create a python virtual environment

virtualenv env

8. Activate

source env/bin/activate

9.  install the python dependencies

pip install -r requirements.txt


10.  create a config.py file in the root directory using the example in the /stubs directory

11. set the FLASK_APP variable

export FLASK_APP = yamz.py

12.  On the first run create the db

flask db init
flask db migrate
flask db upgrade

13. Run the app

flask run