import logging
import sys

from .settings import get_config
from .server import Server


"""
Run this with:

python3 -m consumer.main
"""

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    config = get_config(sys.argv[1:])

    server = Server(config['host'], config['port'])
    server.run()
