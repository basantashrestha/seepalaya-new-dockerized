#!/bin/bash
set -e
#psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
#    CREATE DATABASE pustakalaya;
#    CREATE USER pustakalaya_user WITH PASSWORD 'pustakalaya123';
#    GRANT ALL PRIVILEGES ON DATABASE pustakalaya TO pustakalaya_user;
#EOSQL

# Function to check if the database exists
db_exists() {
    psql -U "$POSTGRES_USER" -tc "SELECT 1 FROM pg_database WHERE datname = 'pustakalaya'" | grep -q 1
}

# Create the database if it does not exist
if ! db_exists; then
    psql -U "$POSTGRES_USER" -c "CREATE DATABASE pustakalaya"
fi

# Create the user and grant privileges
psql -U "$POSTGRES_USER" <<-EOSQL
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'pustakalaya_user') THEN
            CREATE USER pustakalaya_user WITH PASSWORD 'pustakalaya123';
        END IF;
    END
    \$\$;
    GRANT ALL PRIVILEGES ON DATABASE pustakalaya TO pustakalaya_user;
EOSQL

#psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname=pustakalaya < /docker-entrypoint-initdb.d/pustakalaya.sql
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname=pustakalaya < /tmp/pustakalaya.sql


