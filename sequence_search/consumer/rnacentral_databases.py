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

import os
from collections import namedtuple

from sequence_search.consumer.settings import QUERY_DIR, RESULTS_DIR
from .settings import PROJECT_ROOT


RnacentralDatabases = namedtuple("rnacentral_databases", ["id", "label"])

rnacentral_databases = [
    RnacentralDatabases("ena", "ENA"),
    RnacentralDatabases("greengenes", "GreenGenes"),
    RnacentralDatabases("lncrnadb", "lncRNAdb"),
    RnacentralDatabases("mirbase", "miRBase"),
    RnacentralDatabases("pdbe", "PDBe"),
    RnacentralDatabases("pombase", "PomBase"),
    RnacentralDatabases("rdp", "RDP"),
    RnacentralDatabases("refseq", "RefSeq"),
    RnacentralDatabases("rfam", "Rfam"),
    RnacentralDatabases("rgd", "RGD"),
    RnacentralDatabases("sgd", "SGD"),
    RnacentralDatabases("snopy", "snOPY"),
    RnacentralDatabases("srpdb", "SRPDB"),
    RnacentralDatabases("tair", "TAIR"),
    RnacentralDatabases("tmrna_web", "tmRNA Website"),
    RnacentralDatabases("wormbase", "WormBase")
]


def get_database_files():
    """Returns the list of database files in DATABASES_DIRECTORY as pathlib/PosixPath objects"""
    # list of rnacentral databases
    DATABASES_DIRECTORY = PROJECT_ROOT.parent / 'consumer' / 'databases'
    return [file for file in (DATABASES_DIRECTORY).glob('*.fasta')]


def producer_validator(databases):
    database_keys = [ db.id for db in rnacentral_databases ]

    for db in databases:
        if db not in database_keys:
            raise ValueError("Database %s is not a valid RNAcentral database" % db)


def producer_to_consumers_databases(databases):
    """
    If the user submitted a list of databases to process to the producer,
    we might need to do some preprocessing on it, before map-reducing it
    to the consumers. For instance, if user submits `ena`, we need to
    split it into as many chunks, as are present in databases folder.

    Assumes that the list of databases was previously validated by
    producer_validator.

    databases are filename stems like 'ena', 'tmrna-web'
    """
    output = []

    # in case of empty databases list, return output
    if databases == []:
        for file in get_database_files():
            if file.name.startswith('all-except-rrna') or file.name.startswith('whitelist-rrna'):
                output.append(file.name)
    else:
        for database in databases:
            if database == 'ena':  # ena needs to be split into multiple files
                for file in get_database_files():
                    if file.name.startswith('ena'):  # WARNING: this might be overzealous!
                        output.append(file.name)
            else:
                output.append(database + '.fasta')

    return output


def consumer_validator(database):
    ids = [file.name for file in get_database_files()]

    if database not in ids:
        raise ValueError("Database %s is not a valid RNAcentral database" % database)


def query_file_path(job_id, database):
    """Returns path to the file with nhmmer query sequence"""
    return os.path.join(QUERY_DIR, '%s_%s' % (job_id, database))


def result_file_path(job_id, database):
    """Returns path to the file with nhmmer search results"""
    return os.path.join(RESULTS_DIR, '%s_%s' % (job_id, database))


def database_file_path(database):
    """
    Returns path to the file with rnacentral database chunk
    (e.g. ena1.fasta or all-except-rrna1.fasta).
    """
    return PROJECT_ROOT / 'databases' / database
