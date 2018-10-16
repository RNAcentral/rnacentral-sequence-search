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

CONSUMERS = {
    "greengenes": "consumer:8000",
    "pdbe": "consumer:8000",
    "refseq": "consumer:8000",
    "sgd": "consumer:8000",
    "tair": "consumer:8000",
    "lncrnadb": "consumer:8000",
    "pombase": "consumer:8000",
    "rfam": "consumer:8000",
    "snopy": "consumer:8000",
    "tmrna_web": "consumer:8000",
    "mirbase": "consumer:8000",
    "rdp": "consumer:8000",
    "rgd": "consumer:8000",
    "srpdb": "consumer:8000",
    "wormbase": "consumer:8000"
}
