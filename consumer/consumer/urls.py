import pathlib

from consumer.views import index, job


PROJECT_ROOT = pathlib.Path(__file__).parent


def setup_routes(app):
    app.router.add_get('/', index, name='index')
    app.router.add_post('/job/{job_id}', job, name='submit_job')
    setup_static_routes(app)


def setup_static_routes(app):
    app.router.add_static('/static/', path=PROJECT_ROOT / 'static', name='static')
    app.router.add_static('/media/', path=PROJECT_ROOT / 'media', name='media')
