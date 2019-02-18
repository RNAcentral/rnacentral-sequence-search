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
from .filenames import query_file_path, result_file_path


class NhmmerError(Exception):
    """Raise when nhmmer exits with a non-zero status"""
    pass


async def nhmmer_search(sequence, job_id, database):
    sequence = sequence.replace('T', 'U').upper()

    # Set e-values dynamically depending on the query sequence length.
    # The values were computed by searching the full dataset using random short
    # sequences as queries with an extremely high e-value and recording the
    # e-values of the best hit.
    if len(sequence) <= 30:
        e_value = pow(10, 5)
    elif 30 < len(sequence) <= 40:
        e_value = pow(10, 2)
    elif 40 < len(sequence) <= 50:
        e_value = pow(10, -1)
    else:
        e_value = pow(10, -2)

    params = {
        'query': query_file_path(job_id, database),
        'output': result_file_path(job_id, database),
        'nhmmer': settings.NHMMER_EXECUTABLE,
        'db': settings.SEQDATABASES / (database + '.fasta'),
        'cpu': 4,
        'incE': e_value,
        'E': e_value
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
               '--incE {incE} '    # use an E-value of <= X as the inclusion threshold
               '-E {E} '           # report target sequences with an E-value of <= X
               '--rna '            # explicitly specify database alphabet
               '--watson '         # search only top strand
               '--cpu {cpu} '      # number of CPUs to use
               '{query} '          # query file
               '{db}').format(**params)

    process = await asyncio.subprocess.create_subprocess_exec(
        *shlex.split(command),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    output, errors = await process.communicate()
    return_code = process.returncode
    if return_code != 0:
        raise NhmmerError(errors, output, return_code)

    return params['output']