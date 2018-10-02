import os

from aiojobs.aiohttp import spawn
import aiohttp_jinja2
from aiohttp import web, client

from .nhmmer_search import nhmmer_search
from .nhmmer_parse import nhmmer_parse
from .settings import settings


@aiohttp_jinja2.template('index.html')
async def index(request):
    result_filenames = os.listdir(settings.RESULTS_DIR)
    results = [{'id': filename.strip(".txt")[0]} for filename in result_filenames]
    return {'results': results}


async def result(request):
    result_id = request.match_info['result_id']
    filename = settings.RESULTS_DIR / (result_id + ".txt")
    if os.path.isfile(filename) and os.access(filename, os.R_OK):
        return web.FileResponse(filename)
    else:
        return aiohttp_jinja2.render_template('404.html', request, {})


async def submit_job(request):
    """
    For testing purposes, try the following command:

    curl -H "Content-Type:application/json" -d "{\"job_id\": 1, \"databases\": [\"miRBase\"], \"sequence\": \"AAAAGGTCGGAGCGAGGCAAAATTGGCTTTCAAACTAGGTTCTGGGTTCACATAAGACCT\"}" localhost:8000/job
    """
    data = await request.json()
    try:
        job_id = data['job_id']
        databases = data['databases']
        sequence = data['sequence']
        print("job_id = {job_id}, databases = {databases}, sequence = {sequence}".format(
            job_id=job_id,
            databases=databases,
            sequence=sequence)
        )
    except (KeyError, TypeError, ValueError) as e:
        raise web.HTTPBadRequest(text='Bad input') from e

    for database in databases:
        await spawn(request, nhmmer(sequence, job_id, database))

    url = request.app.router['result'].url_for(result_id=str(job_id))
    return web.HTTPFound(location=url)


async def nhmmer(sequence, job_id, database):
    """
    Function that performs nhmmer search and then reports the result to provider API.

    :param sequence: string, e.g. AAAAGGTCGGAGCGAGGCAAAATTGGCTTTCAAACTAGGTTCTGGGTTCACATAAGACCT
    :param job_id:
    :return:
    """

    # TODO: recoverable errors handling
    # TODO: irrecoverable errors handling

    filename = await nhmmer_search(sequence=sequence, job_id=job_id)

    data = []
    for record in nhmmer_parse(filename=filename):
        data.push(record)

    response_url = "{protocol}://{host}:{port}/{url}/{job_id}/{database}".format(
        protocol=settings.PRODUCER_PROTOCOL,
        host=settings.PRODUCER_HOST,
        port=settings.PRODUCER_PORT,
        url=settings.PRODUCER_JOB_DONE_URL,
        job_id=job_id,
        database=database
    )

    client.request(
        'post',
        response_url,
        data=data,
        headers={'content-type': 'application/json'}
    )


    # async with request.app['db'].acquire() as conn:
    #     question_id = int(request.match_info['question_id'])
    #     data = await request.post()
    #     try:
    #         choice_id = int(data['choice'])
    #     except (KeyError, TypeError, ValueError) as e:
    #         raise web.HTTPBadRequest(text='You have not specified choice value') from e
    #     try:
    #         await db.vote(conn, question_id, choice_id)
    #     except db.RecordNotFound as e:
    #         raise web.HTTPNotFound(text=str(e))
    #     router = request.app.router
    #     url = router['results'].url_for(question_id=str(question_id))
    #     return web.HTTPFound(location=url)
