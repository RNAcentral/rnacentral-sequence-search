FROM library/postgres
COPY local_init.sql /docker-entrypoint-initdb.d/