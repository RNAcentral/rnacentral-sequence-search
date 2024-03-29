CREATE USER docker WITH ENCRYPTED PASSWORD 'example';
CREATE DATABASE producer;
GRANT ALL PRIVILEGES ON DATABASE producer TO docker;
ALTER ROLE docker CREATEDB;
CREATE DATABASE test_producer;
GRANT ALL PRIVILEGES ON DATABASE test_producer TO docker;
