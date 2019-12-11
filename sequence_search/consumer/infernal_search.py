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
from sequence_search.consumer.settings import INFERNAL_QUERY_DIR, INFERNAL_RESULTS_DIR


async def infernal_search(sequence, job_id):
    """
    Run cmscan to search the CM-format Rfam database
    :param sequence: sequence to search
    :param job_id: id of the job
    :return:
    """
    sequence = sequence.replace('T', 'U').upper()

    params = {
        'query': os.path.join(INFERNAL_QUERY_DIR, '%s' % job_id),
        'output': os.path.join(INFERNAL_RESULTS_DIR, '%s' % job_id),
        'rfam_cm': settings.RFAM_CM,
        'clanin': settings.CLANIN,
        'cmscan': settings.CMSCAN_EXECUTABLE,
        'cpu': 4,
    }

    # write out query in fasta format
    with open(params['query'], 'w') as f:
        f.write('>query\n')
        f.write(sequence)
        f.write('\n')

    command = ('{cmscan} '
               '--notextw '          # unlimit ASCII text output line width
               '--cut_ga '           # use CM's GA gathering cutoffs as reporting thresholds
               '--rfam '             # set heuristic filters at Rfam-level (fast)
               '--nohmmonly '        # never run HMM-only mode, not even for models with 0 basepairs
               '--fmt 2 '            # set hit table format to 2
               '--tblout {output} '  # save parseable table of hits to file
               '--acc '              # prefer accessions over names in output
               '--cpu {cpu} '        # number of CPUs to use
               '--clanin {clanin} '  # read clan information from file
               '--oskip '            # w/'--fmt 2' and '--tblout', do not output lower scoring overlaps
               '{rfam_cm} '          # Rfam.cm file
               '{query} '            # query file
               ).format(**params)

    process = await asyncio.subprocess.create_subprocess_exec(
        *shlex.split(command),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    return process, params['output']
