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

# TODO: get the bds from elsewhere and not leave them hard coded
rnacentral_databases = [
    RnacentralDatabases("dictybase", "dictyBase"),
    RnacentralDatabases("ena", "ENA"),
    RnacentralDatabases("ensembl", "Ensembl"),
    RnacentralDatabases("ensembl_fungi", "Ensembl Fungi"),
    RnacentralDatabases("ensembl_metazoa", "Ensembl Metazoa"),
    RnacentralDatabases("ensembl_plants", "Ensembl Plants"),
    RnacentralDatabases("ensembl_protists", "Ensembl Protists"),
    RnacentralDatabases("flybase", "FlyBase"),
    RnacentralDatabases("gencode", "GENCODE"),
    RnacentralDatabases("greengenes", "GreenGenes"),
    RnacentralDatabases("gtrnadb", "GtRNAdb"),
    RnacentralDatabases("hgnc", "HGNC"),
    RnacentralDatabases("lncbase", "LncBase"),
    RnacentralDatabases("lncbook", "LncBook"),
    RnacentralDatabases("lncipedia", "LNCipedia"),
    RnacentralDatabases("lncrnadb", "lncRNAdb"),
    RnacentralDatabases("mgi", "MGI"),
    RnacentralDatabases("mirbase", "miRBase"),
    RnacentralDatabases("modomics", "Modomics"),
    RnacentralDatabases("noncode", "NONCODE"),
    RnacentralDatabases("pdbe", "PDBe"),
    RnacentralDatabases("pombase", "PomBase"),
    RnacentralDatabases("rdp", "RDP"),
    RnacentralDatabases("refseq", "RefSeq"),
    RnacentralDatabases("rfam", "Rfam"),
    RnacentralDatabases("rgd", "RGD"),
    RnacentralDatabases("sgd", "SGD"),
    RnacentralDatabases("silva", "SILVA"),
    RnacentralDatabases("snopy", "snOPY"),
    RnacentralDatabases("srpdb", "SRPDB"),
    RnacentralDatabases("tair", "TAIR"),
    RnacentralDatabases("tarbase", "TarBase"),
    RnacentralDatabases("tmrna_web", "tmRNA Website"),
    RnacentralDatabases("wormbase", "WormBase"),
    RnacentralDatabases("zwd", "ZWD")
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

    if databases:
        # new fasta files have been split into files up to 150 MB;
        # therefore, we can now have more than one file for each database. 
        for database in databases:
            for file in get_database_files():
                if file.name.startswith(database):
                    output.append(file.name)
    else:
        # in case of empty databases list, use all-except-rrna and whitelist-rrna fasta files
        for file in get_database_files():
            if file.name.startswith('all-except-rrna') or file.name.startswith('whitelist-rrna'):
                output.append(file.name)

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
