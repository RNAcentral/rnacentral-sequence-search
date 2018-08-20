import logging
import sys


from .settings import get_config
from .server import Server


def main(argv):
    logging.basicConfig(level=logging.DEBUG)

    config = get_config(argv)

    server = Server(config['host'], config['port'])
    server.run()


if __name__ == '__main__':
    main(sys.argv[1:])
