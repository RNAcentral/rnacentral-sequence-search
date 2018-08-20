import pathlib

from .views import index, submit_job, result
from .settings import PROJECT_ROOT

def setup_routes(app):
    app.router.add_get('/', index, name='index')
    app.router.add_get('/results/{result_id}', result, name='result')
    app.router.add_post('/job/{job_id}', submit_job, name='submit_job')
    setup_static_routes(app)


def setup_static_routes(app):
    app.router.add_static('/static/', path=PROJECT_ROOT / 'static', name='static')
