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


RnacentralDatabases = namedtuple("rnacentral_databases", ["id", "label", "e_value"])

# TODO: get the bds and e-value from elsewhere and not leave them hard coded
rnacentral_databases = [
    RnacentralDatabases("5srrnadb", "5SrRNAdb", 1.367736),
    RnacentralDatabases("crw", "CRW", 1.195812),
    RnacentralDatabases("dictybase", "dictyBase", 0.014499),
    RnacentralDatabases("ena", "ENA", 11346.105873),
    RnacentralDatabases("ensembl", "Ensembl", 1217.994276),
    RnacentralDatabases("ensembl_fungi", "Ensembl Fungi", 3.336983),
    RnacentralDatabases("ensembl_gencode", "Ensembl/GENCODE", 79.642297),
    RnacentralDatabases("ensembl_metazoa", "Ensembl Metazoa", 34.845222),
    RnacentralDatabases("ensembl_plants", "Ensembl Plants", 25.915263),
    RnacentralDatabases("ensembl_protists", "Ensembl Protists", 1.845517),
    RnacentralDatabases("flybase", "FlyBase", 3.429574),
    RnacentralDatabases("genecards", "GeneCards", 305.92219),
    RnacentralDatabases("greengenes", "GreenGenes", 1423.553627),
    RnacentralDatabases("gtrnadb", "GtRNAdb", 18.26),
    RnacentralDatabases("hgnc", "HGNC", 7.575653),
    RnacentralDatabases("lncbase", "LncBase", 0.029263),
    RnacentralDatabases("lncbook", "LncBook", 403.980845),
    RnacentralDatabases("lncipedia", "LNCipedia", 194.814831),
    RnacentralDatabases("lncrnadb", "lncRNAdb", 0.191325),
    RnacentralDatabases("malacards", "MalaCards", 55.417018),
    RnacentralDatabases("mgi", "MGI", 14.605057),
    RnacentralDatabases("mirbase", "miRBase", 4.657073),
    RnacentralDatabases("mirgenedb", "MirGeneDB", 1.669902),
    RnacentralDatabases("modomics", "Modomics", 0.050331),
    RnacentralDatabases("noncode", "NONCODE", 265.434743),
    RnacentralDatabases("pdbe", "PDBe", 1.098222),
    RnacentralDatabases("pirbase", "piRBase", 6.049478),
    RnacentralDatabases("pombase", "PomBase", 1.941092),
    RnacentralDatabases("rdp", "RDP", 9.366837),
    RnacentralDatabases("refseq", "RefSeq", 68.47133),
    RnacentralDatabases("rfam", "Rfam", 322.77),
    RnacentralDatabases("rgd", "RGD", 26.121729),
    RnacentralDatabases("sgd", "SGD", 0.062898),
    RnacentralDatabases("silva", "SILVA", 8584.630466),
    RnacentralDatabases("snodb", "snoDB", 0.23168),
    RnacentralDatabases("snopy", "snOPY", 0.295894),
    RnacentralDatabases("snorna_database", "snoRNA Database", 0.036421),
    RnacentralDatabases("srpdb", "SRPDB", 0.133472),
    RnacentralDatabases("tair", "TAIR", 1.865084),
    RnacentralDatabases("tarbase", "TarBase", 0.032912),
    RnacentralDatabases("tmrna_web", "tmRNA Website", 4.017364),
    RnacentralDatabases("wormbase", "WormBase", 4.577316),
    RnacentralDatabases("zfin", "ZFIN", 0.954655),
    RnacentralDatabases("zwd", "ZWD", 4.329375)
]


def get_database_files():
    """Returns the list of database files in DATABASES_DIRECTORY as pathlib/PosixPath objects"""
    # list of rnacentral databases
    DATABASES_DIRECTORY = PROJECT_ROOT.parent / 'consumer' / 'databases'
    return [file for file in (DATABASES_DIRECTORY).glob('*.fasta')]


def producer_validator(databases):
    database_keys = [db.id for db in rnacentral_databases]

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


def get_e_value(database):
    """Return the e-value for a specific database"""
    e_value = None
    for item in rnacentral_databases:
        if item.id.startswith(database):
            e_value = item.e_value
            break
    return e_value
