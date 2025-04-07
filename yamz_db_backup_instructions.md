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
   createdb yamz_prd
   ```

2. Restore the database from the dump file:
   ```
   pg_restore -d yamz_prd -h localhost -U your_postgres_username -W -v yamz_prd_backup.dump
   ```
   
   The command will prompt for your password.

3. Verify the restore was successful:
   ```
   psql -h localhost -U your_postgres_username -d yamz_prd -c "SELECT count(*) FROM users;"
   ```

### Update Local Configuration

Update your local application configuration to point to the restored database:

```python
SQLALCHEMY_DATABASE_URI = "postgresql://your_postgres_username:your_password@localhost/yamz_prd"
```

## Troubleshooting

- If you encounter permission issues during restore, ensure your PostgreSQL user has sufficient privileges
- For role errors, you may need to create missing roles first:
  ```
  createuser -h localhost -U postgres -P -s rolename
  ```
- For schema conflicts, you might need to drop the existing database first:
  ```
  dropdb -h localhost -U postgres yamz_prd
