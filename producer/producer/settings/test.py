import os

# hostname to listen on
HOST = 'localhost'

# TCP port for the server to listen on
PORT = 8002

# postgres database settings
POSTGRES_HOST = 'postgres'
POSTGRES_PORT = 5432
POSTRGES_DATABASE = 'producer'
POSTGRES_USER = 'docker'
POSTGRES_PASSWORD = os.getenv('POSTRGES_PASSWORD')
