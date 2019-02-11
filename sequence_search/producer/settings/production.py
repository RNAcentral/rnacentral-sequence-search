import os


# hostname to listen on
HOST = "0.0.0.0"

# TCP port for the server to listen on
PORT = 8002

# postgres database settings
POSTGRES_HOST = '192.168.0.6'
POSTGRES_PORT = 5432
POSTGRES_DATABASE = 'producer'
POSTGRES_USER = 'docker'
POSTGRES_PASSWORD = os.getenv('POSTRGES_PASSWORD', 'pass')

CONSUMER_PORT = '8000'
CONSUMER_IPS = [
    "192.168.0.7",
    "192.168.0.8",
    "192.168.0.9",
    "192.168.0.10",
    "192.168.0.11",
    "192.168.0.12",
    "192.168.0.13",
    "192.168.0.14",
    "192.168.0.15",
    "192.168.0.16",
    # "192.168.0.17",
    # "192.168.0.18",
    # "192.168.0.19",
    # "192.168.0.20",
    # "192.168.0.21",
    # "192.168.0.22",
    # "192.168.0.23",
    # "192.168.0.24",
    # "192.168.0.25",
    # "192.168.0.26"
]
