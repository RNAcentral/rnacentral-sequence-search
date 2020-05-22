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
import re
from itertools import islice


def infernal_parse(filename):
    """
    Get data from the deoverlapped file
    :param filename: file to parse, named with job_id
    :return: data to save in the database
    """
    lines = []
    with open(filename, 'r') as file:
        for line in file.readlines():
            if not line.startswith('#'):
                line = re.sub(" +", " ", line).strip()
                lines.append(line.split(" "))

    results = []
    for item in lines:
        result = {
            "target_name": item[0],
            "accession_rfam": item[1],
            "query_name": item[2],
            "accession_seq": item[3],
            "mdl": item[4],
            "mdl_from": item[5],
            "mdl_to": item[6],
            "seq_from": item[7],
            "seq_to": item[8],
            "strand": item[9],
            "trunc": item[10],
            "pipeline_pass": item[11],
            "gc": item[12],
            "bias": item[13],
            "score": item[14],
            "e_value": item[15],
            "inc": item[16],
            "description": ' '.join(item[17:])
        }
        results.append(result)

    return results


def alignment(filename):
    """
    Get the alignment from the output file
    :param filename: file to parse, named with job_id
    :return: alignment to save in the database. Values are used to find the infernal result
    """
    output = []
    with open(filename, 'r') as file:
        for line in file:
            if line.startswith('>>'):
                get_accession = line.split(' ')
                values = ''.join(islice(file, 2, 3))
                values = list(filter(None, values.split(' ')))
                alignment = ''.join(islice(file, 7))

                output_result = {
                    "accession_rfam": get_accession[1],
                    "mdl_from": values[6],
                    "mdl_to": values[7],
                    "seq_from": values[9],
                    "seq_to": values[10],
                    "gc": values[15],
                    "score": values[3],
                    "e_value": values[2],
                    "alignment": alignment
                }
                output.append(output_result)

    return output
