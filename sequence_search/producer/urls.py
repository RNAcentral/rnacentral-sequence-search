"""
Copyright [2009-2019] EMBL-European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from aiohttp_swagger import setup_swagger
from .views import index, submit_job, job_status, job_result, rnacentral_databases, job_results_urs_list, \
    facets, facets_search, list_rnacentral_ids, post_rnacentral_ids
from . import settings


def setup_routes(app):
    app.router.add_post('/api/submit-job', submit_job, name='submit-job')
    app.router.add_get('/api/job-status/{job_id:[A-Za-z0-9_-]+}', job_status, name='job-status')
    app.router.add_get('/api/job-result/{job_id:[A-Za-z0-9_-]+}', job_result, name='job-result')
    app.router.add_get('/api/rnacentral-databases', rnacentral_databases, name='rnacentral-databases')
    app.router.add_get('/api/job-results-urs-list/{job_id:[A-Za-z0-9_-]+}', job_results_urs_list, name='job-results-urs-list')
    app.router.add_get('/api/facets/{job_id:[A-Za-z0-9_-]+}', facets, name='facets')
    app.router.add_get('/api/facets-search/{job_id:[A-Za-z0-9_-]+}', facets_search, name='facets-search')
    app.router.add_get('/api/list-rnacentral-ids/{job_id:[A-Za-z0-9_-]+}', list_rnacentral_ids, name='list-rnacentral-ids'),
    app.router.add_post('/api/post-rnacentral-ids/{job_id:[A-Za-z0-9_-]+}', post_rnacentral_ids, name='post-rnacentral-ids')
    setup_static_routes(app)

    # setup swagger documentation
    setup_swagger(app, swagger_url="api/doc")

    # cover-all index url goes last, even after swagger
    app.router.add_get('/{tail:.*}', index, name='index')


def setup_static_routes(app):
    app.router.add_static('/dist/', path=settings.PROJECT_ROOT / 'static' / 'dist', name='static')
