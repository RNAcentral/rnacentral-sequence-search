import logging
import aiohttp


class ConsumerClient(object):
    async def submit_job(self, url, json_data, headers):
        async with aiohttp.ClientSession() as session:
            logging.debug("Queuing JobChunk to consumer: url = {}, json_data = {}, headers = {}"
                          .format(url, json_data, headers))

            response = await session.post(url, data=json_data, headers=headers)
            return response
