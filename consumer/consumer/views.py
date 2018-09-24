import asyncio
from aiojobs.aiohttp import spawn
import aiohttp_jinja2
from aiohttp import web
import os

from .settings import settings


@aiohttp_jinja2.template('index.html')
async def index(request):
    results = os.listdir(settings.RESULTS_DIR)
    return {'results': results}


async def result(request, result_id):
    try:
        result = open(settings.RESULTS_DIR / result_id / "output.txt")
    except :
        response = aiohttp_jinja2.render_template('404.html', request, {})


async def submit_job(request):
    data = await request.json()
    try:
        job_id = data['job_id']
        databases = data['databases']
        sequence = data['sequence']
        print("job_id = {job_id}, databases = {databases}, sequence = {sequence}".format(job_id=job_id, databases=databases, sequence=sequence))
    except (KeyError, TypeError, ValueError) as e:
        raise web.HTTPBadRequest(text='Bad input') from e

    await spawn(request, nhmmer())

    url = request.app.router['result'].url_for(result_id=str(job_id))
    return web.HTTPFound(location=url)


async def nhmmer():
    await asyncio.sleep(1)
    return


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
