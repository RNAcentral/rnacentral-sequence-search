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
                line = re.sub(" +", " ", line)
                lines.append(line.split(" "))

    results = []
    for item in lines:
        result = {
            "target_name": item[1],
            "accession_rfam": item[2],
            "query_name": item[3],
            "accession_seq": item[4],
            "clan_name": item[5],
            "mdl": item[6],
            "mdl_from": item[7],
            "mdl_to": item[8],
            "seq_from": item[9],
            "seq_to": item[10],
            "strand": item[11],
            "trunc": item[12],
            "pipeline_pass": item[13],
            "gc": item[14],
            "bias": item[15],
            "score": item[16],
            "e_value": item[17],
            "inc": item[18],
            "olp": item[19],
            "anyidx": item[20],
            "afrct1": item[21],
            "afrct2": item[22],
            "winidx": item[23],
            "wfrct1": item[24],
            "wfrct2": item[25],
            "description": ' '.join(item[26:])
        }
        results.append(result)

    return results
