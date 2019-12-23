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
import os
import shlex
import asyncio.subprocess

from . import settings
from sequence_search.consumer.settings import INFERNAL_RESULTS_DIR


async def infernal_deoverlap(job_id):
    params = {
        'file': os.path.join(INFERNAL_RESULTS_DIR, '%s' % job_id),
        'output': os.path.join(INFERNAL_RESULTS_DIR, '%s.deoverlapped' % job_id),
        'cmsearch-deoverlap': settings.DEOVERLAP,
    }

    command = ('{cmsearch-deoverlap} '
               '--maxkeep '             # keep hits that only overlap with other hits that are not kept
               '--cmscan '              # tblout files are from cmscan v1.1x, not cmsearch
               '--overlapout '          # create new tabular file with overlap information in 'output'
               'output '                # file deoverlapped
               '{file} '                # cmscan results
               ).format(**params)

    process = await asyncio.subprocess.create_subprocess_exec(
        *shlex.split(command),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    return process, params['output']
