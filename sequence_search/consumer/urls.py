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

from .views import index, result, submit_job, submit_infernal_job
from . import settings


def setup_routes(app):
    app.router.add_get('/', index, name='index')
    app.router.add_get('/results/{result_id}', result, name='result')
    app.router.add_post('/submit-job', submit_job, name='submit-job')
    app.router.add_post('/submit-infernal-job', submit_infernal_job, name='submit-infernal-job')
    setup_static_routes(app)


def setup_static_routes(app):
    app.router.add_static('/static/', path=settings.PROJECT_ROOT / 'static', name='static')
