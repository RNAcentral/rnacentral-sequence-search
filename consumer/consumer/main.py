import logging
import sys


from consumer.settings import get_config
from consumer.server import Server


def main(argv):
    logging.basicConfig(level=logging.DEBUG)

    config = get_config(argv)

    server = Server(config['host'], config['port'])
    server.run()

if __name__ == '__main__':
    main(sys.argv[1:])
