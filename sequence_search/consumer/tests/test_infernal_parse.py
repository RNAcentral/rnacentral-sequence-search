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
import unittest

from sequence_search.consumer.infernal_parse import infernal_parse
from sequence_search.consumer.settings.__init__ import PROJECT_ROOT


class InfernalParseTestCase(unittest.TestCase):
    async def test_infernal_parse(self):
        file = PROJECT_ROOT / 'tests' / 'tblout_file'
        data = [
            {'target_name': '5S_rRNA',
             'accession_rfam': 'RF00001',
             'query_name': 'query',
             'accession_seq': '-',
             'mdl': 'cm', 'mdl_from': '1',
             'mdl_to': '119',
             'seq_from': '1',
             'seq_to': '119',
             'strand': '+',
             'trunc': 'no',
             'pipeline_pass': '1',
             'gc': '0.49',
             'bias': '0.0',
             'score': '104.9',
             'e_value': '3.2e-24',
             'inc': '!',
             'description': '5S ribosomal RNA'}
        ]
        results = infernal_parse(file)
        assert results == data
