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

import aiohttp_jinja2
import os

from .. import settings


@aiohttp_jinja2.template('index.html')
async def index(request):
    try:
        path = os.path.exists(settings.PROJECT_ROOT / 'static' / 'rnacentral-sequence-search-embed')
    except FileNotFoundError:
        path = None
    return {'path': path}
