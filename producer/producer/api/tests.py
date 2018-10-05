# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

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

from django.conf import settings
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from .models import Job


class JobDone(APITestCase):
    def test_submit_job_post_success(self):
        c = APIClient()
        url = reverse('submit-job')
        response = c.post(url, data={"query": "ACGCTGATGCTAGTGCGATGCTA", "databases": ["mirbase"]})
        self.assertEqual(response.status_code, 201)

    def test_job_done_post_success(self):
        # prepare job object to submit this job chunk into it
        job = Job.objects.create(query="ACGCTGATGCTAGTGCGATGCTA", databases=["mirbase"])

        c = APIClient()
        url = reverse('job-done')
        response = c.post(url, data={"job_id": job.id, "database": "mirbase", "result": "asdfjasdjfajsdfjasjdfjasdjfa"})
        if response.status_code != 201:
            self.assertEqual(response.status_code, 201)
