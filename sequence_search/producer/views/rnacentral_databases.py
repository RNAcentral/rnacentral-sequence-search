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

from aiohttp import web
from aiojobs.aiohttp import atomic

from ...consumer.rnacentral_databases import rnacentral_databases as databases


@atomic
async def rnacentral_databases(request):
    """Sends a list of rnacentral databases from backend to frontend."""
    output = [{"id": db.id, "label": db.label} for db in databases]
    return web.json_response(output)
