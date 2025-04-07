# YAMZ Database Backup and Restore Instructions

## About This Backup

- **Filename:** `yamz_prd_backup.dump`
- **Size:** 3.5MB
- **Format:** PostgreSQL custom format (compressed)
- **Database:** yamz_prd
- **Created on:** April 7, 2025

## Downloading the Backup

You can download the backup file from the server using:
- SCP: `scp username@server:/home/yamz/prd/yamz/yamz_prd_backup.dump /path/to/local/destination`
- SFTP tool of your choice
- Or through your file browser if you have mounted the remote server

## Restoring to Local PostgreSQL

### Prerequisites

1. PostgreSQL installed on your local machine
2. Sufficient privileges to create databases

### Restore Steps

1. Create a new database on your local PostgreSQL server:
   ```
   createdb -U postgres -h localhost yamz_prd
   ```

2. Restore the database from the dump file:
   ```
   pg_restore -d yamz_prd -h localhost -U postgres -v yamz_prd_backup.dump
   ```
   
   The command will prompt for your password.

3. Verify the restore was successful:
   ```
   psql -U postgres -h localhost -d yamz_prd -c "SELECT count(*) FROM users;"
   psql -U postgres -h localhost -d yamz_prd -c "SELECT count(*) FROM terms;"
   ```

### Update Local Configuration

The application configuration (_config.py) should already be set to use the restored database:

```python
SQLALCHEMY_DATABASE_URI = (
    os.environ.get("SQL_ALCHEMY_DATABASE_URI")
    or "postgresql://postgres:PASS@localhost/yamz_prd"
)
```

Replace "PASS" with your actual PostgreSQL password or set the SQL_ALCHEMY_DATABASE_URI environment variable.

## Troubleshooting

- If you encounter permission issues during restore, ensure your PostgreSQL user has sufficient privileges
- For role errors, you may need to create missing roles first:
  ```
  createuser -h localhost -U postgres -P -s rolename
  ```
- For schema conflicts, you might need to drop the existing database first:
  ```
  dropdb -h localhost -U postgres yamz_prd
