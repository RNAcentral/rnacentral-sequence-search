import logging
import asyncio
import aiohttp
from aiohttp import test_utils, web

from .settings import ENVIRONMENT


class ProducerClient(object):
    async def return_results(self, url, json_data, headers):
        logger = logging.Logger('aiohttp.web')
        if ENVIRONMENT != 'TEST':
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=json_data, headers=headers) as response:
                    if response.status != 200:
                        text = await response.text()
                        logger.error('Job %s failed to deliver results: %s' % (job_id, text))
                    else:
                        logger.info('Results of job %s passed to' % response.status)
        else:
            # in TEST environment mock the request
            logging.debug("Queuing JobChunk to consumer: url = {}, json_data = {}, headers = {}"
                          .format(url, json_data, headers))

            request = test_utils.make_mocked_request('POST', url, headers=headers)
            await asyncio.sleep(1)
            response = web.Response(status=200)

        return response
