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

from shutil import copyfile

from sequence_search.consumer.infernal_deoverlap import infernal_deoverlap
from sequence_search.consumer.settings.__init__ import PROJECT_ROOT


class InfernalDeoverlapTestCase(unittest.TestCase):
    async def test_infernal_deoverlap(self):
        src = PROJECT_ROOT / 'tests' / 'tblout_file'
        dst = PROJECT_ROOT / 'infernal-results' / 'tblout_file'
        copyfile(src, dst)

        process_deoverlap, file_deoverlap = await infernal_deoverlap(job_id='tblout_file')
        assert process_deoverlap != 0
        assert 'tblout_file.deoverlapped' in file_deoverlap
