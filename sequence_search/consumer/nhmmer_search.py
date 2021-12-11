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

import shlex
import asyncio.subprocess

from . import settings
from sequence_search.consumer.rnacentral_databases import query_file_path, result_file_path, database_file_path, \
    get_e_value


class NhmmerError(Exception):
    """Raise when nhmmer exits with a non-zero status"""
    pass


async def nhmmer_search(sequence, job_id, database):
    sequence = sequence.replace('T', 'U').upper()

    try:
        if database.startswith('all-except-rrna') or database.startswith('whitelist-rrna'):
            db_name = None
        else:
            db_name = database.split('-')[0]
    except ValueError:
        db_name = None

    e_value = get_e_value(db_name) if db_name else 3990.116525

    params = {
        'query': query_file_path(job_id, database),
        'output': result_file_path(job_id, database),
        'nhmmer': settings.NHMMER_EXECUTABLE,
        'db': database_file_path(database),
        'e_value': e_value,
        'cpu': 4,
        'f3': '--F3 0.02' if len(sequence) < 50 else ''
    }

    # write out query in fasta format
    with open(params['query'], 'w') as f:
        f.write('>query\n')
        f.write(sequence)
        f.write('\n')

    command = ('{nhmmer} '
               '--qfasta '         # query format
               '--tformat fasta '  # target format
               '-o {output} '      # direct main output to a file
               '-T 0 '             # report sequences >= this score threshold in output
               '{f3} '             # stage 3 (Fwd) threshold: promote hits w/ P <= F3
               '--rna '            # explicitly specify database alphabet
               '--watson '         # search only top strand
               '--cpu {cpu} '      # number of CPUs to use
               '-Z {e_value} '     # set database size (Megabases) for E-value calculations
               '{query} '          # query file
               '{db}').format(**params)

    process = await asyncio.subprocess.create_subprocess_exec(
        *shlex.split(command),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    return process, params['output']
