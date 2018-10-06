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

import sqlalchemy as sa


STATUS_CHOICES = (
    ('started', 'started'),
    ('success', 'success'),
    ('failed', 'failed'),
)

metadata = sa.MetaData()


jobs = sa.Table('jobs', metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Colum('query', sa.Text),
                 sa.Column('databases', sa.String(255)),  # should be array of Strings with choices=DATABASE_CHOICES
                 sa.Column('submitted', sa.DateTime),
                 sa.Column('finished', sa.DateTime),
                 sa.Column('status', sa.String(255)))  # choices=STATUS_CHOICES, default='started'

"""Part of the search job, run against a specific database and assigned to a specific consumer"""
job_chunks = sa.Table('job_chunks', metadata,
                  sa.Column('id', sa.Integer, primary_key=True),
                  sa.Column('job_id', None, sa.ForeignKey('users.id')),
                  sa.Column('database', sa.String(255)),
                  sa.Column('result', sa.String(255), nullable=True),
                  sa.Column('status', sa.String(255), nullable=False))  # choices=STATUS_CHOICES, default='started'
