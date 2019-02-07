import logging
import json
import asyncio
import aiohttp
from aiohttp import test_utils, web

from .settings import ENVIRONMENT


class ProducerClient(object):
    async def report_job_chunk_done(self, url, headers, job_id, database):
        logger = logging.Logger('aiohttp.web')

        json_data = json.dumps({'job_id': job_id, 'database': database})

        if ENVIRONMENT != 'TEST':
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=json_data, headers=headers) as response:
                    if response.status != 200 and response.status != 201:
                        text = await response.text()
                        logger.error('JobChunk with job_id = %s, database = %s failed to deliver results: %s' % (job_id, database, text))
                    else:
                        logger.info('JobChunk with job_id = %s, database = %s returned results: %s' % (job_id, database, response.status))
        else:
            # in TEST environment mock the request
            logging.debug("Queuing JobChunk to consumer: url = {}, json_data = {}, headers = {}"
                          .format(url, json_data, headers))

            request = test_utils.make_mocked_request('POST', url, headers=headers)
            await asyncio.sleep(1)
            response = web.Response(status=200)

        return response
