import os

from . import PROJECT_ROOT


# hostname to listen on
HOST = "0.0.0.0"

# TCP port for the server to listen on
PORT = 8002

# postgres database settings
POSTGRES_HOST = 'postgres'
POSTGRES_PORT = 5432
POSTGRES_DATABASE = 'producer'
POSTGRES_USER = 'docker'
POSTGRES_PASSWORD = os.getenv('POSTRGES_PASSWORD')


CONSUMERS = {
    "greengenes": "192.168.0.7:8000",
    "pdbe": "192.168.0.8:8000",
    "refseq": "192.168.0.9:8000",
    "sgd": "192.168.0.10:8000",
    "tair": "192.168.0.11:8000",
    "lncrnadb": "192.168.0.12:8000",
    "pombase": "192.168.0.13:8000",
    "rfam": "192.168.0.14:8000",
    "snopy": "192.168.0.15:8000",
    "tmrna_web": "192.168.0.16:8000",
    "mirbase": "192.168.0.17:8000",
    "rdp": "192.168.0.18:8000",
    "rgd": "192.168.0.19:8000",
    "srpdb": "192.168.0.20:8000",
    "wormbase": "192.168.0.21:8000"
}