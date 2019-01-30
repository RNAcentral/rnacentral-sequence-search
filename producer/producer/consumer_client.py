import logging
import asyncio
import aiohttp
from aiohttp import test_utils, web

from .settings import ENVIRONMENT


class ConsumerClient(object):
    async def submit_job(self, url, json_data, headers):
        if ENVIRONMENT != 'TEST':
            async with aiohttp.ClientSession() as session:
                logging.debug("Queuing JobChunk to consumer: url = {}, json_data = {}, headers = {}"
                              .format(url, json_data, headers))

                response = await session.post(url, data=json_data, headers=headers)
        else:
            # in TEST environment mock the request
            logging.debug("Queuing JobChunk to consumer: url = {}, json_data = {}, headers = {}"
                          .format(url, json_data, headers))

            request = test_utils.make_mocked_request('POST', url, headers=headers)
            await asyncio.sleep(1)
            response = web.Response(status=200)

        return response
