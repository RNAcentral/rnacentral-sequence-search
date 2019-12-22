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


def infernal_parse(filename):
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
