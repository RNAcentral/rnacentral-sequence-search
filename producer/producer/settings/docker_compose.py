import os

# hostname to listen on
HOST = '0.0.0.0'

# TCP port for the server to listen on
PORT = 8002

# postgres database settings
POSTGRES_HOST = 'postgres'
POSTGRES_PORT = 5432
POSTGRES_DATABASE = 'producer'
POSTGRES_USER = 'docker'
POSTGRES_PASSWORD = 'example'

CONSUMER_PORT = '8000'
CONSUMER_IPS = ["consumer"]
