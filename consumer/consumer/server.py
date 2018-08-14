import asyncio
from concurrent.futures import ThreadPoolExecutor
from collections import deque


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.pool = ThreadPoolExecutor(max_workers=10)
        self.loop = asyncio.get_event_loop()
        self.data = deque([])
