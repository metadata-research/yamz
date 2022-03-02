
# YAMZ Metadata Dictionary

This is the README for the YAMZ metadictionary and includes instructions for
deploying on a local machine for testing and on a Linux based environment for a
scalable production version. These assume a Ubuntu GNU/Linux environment, but
should be easily adaptable to any system; YAMZ is written in Python and uses
only cross-platform packages.

The current application requires the use of a postgres database to support full text search. 

The following is an example configuration. You can substitute your own db names and users


1) Install postgres. Installation instructions may vary depending on the platform.

[amc](https://www.postgresql.org/download/macosx/)

2. Create a database in psql
   
postgres=# create database yamz with owner postgres;


2. Switch to that db

postgres=# \c yamz;


3. Create a user
   
yamz=# create user contributor with encrypted password 'PASS';


5. Clone the repository

git clone https://github.com/metadata-research/yamz.git

