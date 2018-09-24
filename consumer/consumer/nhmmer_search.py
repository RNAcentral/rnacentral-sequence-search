"""
Copyright [2009-2017] EMBL-European Bioinformatics Institute
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

from .settings import settings


class NhmmerError(Exception):
    """Raise when nhmmer exits with a non-zero status"""
    pass


def get_e_value(sequence):
    """
    Set E-values dynamically depending on the query sequence length.
    The values were computed by searching the full dataset
    using random short sequences as queries
    with an extremely high E-value and recording
    the E-values of the best hit.
    """
    length = len(sequence)

    if length <= 30:
        e_value = pow(10, 5)
    elif 30 < length <= 40:
        e_value = pow(10, 2)
    elif 40 < length <= 50:
        e_value = pow(10, -1)
    else:
        e_value = pow(10, -2)

    return e_value


def create_query_file(params, sequence):
    """Write out query in fasta format."""
    with open(params['query'], 'w') as f:
        f.write('>query\n')
        f.write(sequence)
        f.write('\n')


def get_command(params):
    """Get nhmmer command."""
    return


async def run_nhmmer(params):
    """Launch nhmmer."""
    command = ('{nhmmer} '
               '--qformat fasta '  # query format
               '--tformat fasta '  # target format
               '-o {output} '  # direct main output to a file
               '--incE {incE} '  # use an E-value of <= X as the inclusion threshold
               '-E {E} '  # report target sequences with an E-value of <= X
               '--rna '  # explicitly specify database alphabet
               '--toponly '  # search only top strand
               '--cpu {cpu} '  # number of CPUs to use
               '{query} '  # query file
               '{db}').format(params)

    process = await asyncio.subprocess.create_subprocess_exec(
        shlex.split(command),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    output, errors = await process.communicate()
    return_code = process.returncode
    if return_code != 0:
        raise NhmmerError(errors, output, return_code)


async def nhmmer_search(sequence, job_id):
    # Initialize internal variables.
    sequence = sequence.replace('T', 'U').upper()
    e_value = get_e_value(sequence)
    params = {
        'query': os.path.join(settings.QUERY_DIR, '%s.fasta' % job_id),
        'output': os.path.join(settings.RESULTS_DIR, '%s.txt' % job_id),
        'nhmmer': settings.NHMMER_EXECUTABLE,
        'db': settings.SEQDATABASE,
        'cpu': 4,
        'incE': e_value,
        'E': e_value
    }

    create_query_file(params, sequence)
    await run_nhmmer(params)

    return params['output']
