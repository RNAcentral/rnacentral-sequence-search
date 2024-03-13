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
    RnacentralDatabases("5srrnadb", "5SrRNAdb", 1.36),
    RnacentralDatabases("crw", "CRW", 1.19),
    RnacentralDatabases("dictybase", "dictyBase", 0.01),
    RnacentralDatabases("ena", "ENA", 14166.52),
    RnacentralDatabases("ensembl", "Ensembl", 2227.93),
    RnacentralDatabases("ensembl_fungi", "Ensembl Fungi", 4.78),
    RnacentralDatabases("ensembl_gencode", "Ensembl/GENCODE", 100.04),
    RnacentralDatabases("ensembl_metazoa", "Ensembl Metazoa", 596.31),
    RnacentralDatabases("ensembl_plants", "Ensembl Plants", 32.43),
    RnacentralDatabases("ensembl_protists", "Ensembl Protists", 1.84),
    RnacentralDatabases("flybase", "FlyBase", 3.46),
    RnacentralDatabases("genecards", "GeneCards", 801.80),
    RnacentralDatabases("greengenes", "GreenGenes", 1423.55),
    RnacentralDatabases("gtrnadb", "GtRNAdb", 18.27),
    RnacentralDatabases("hgnc", "HGNC", 9.66),
    RnacentralDatabases("lncbase", "LncBase", 0.03),
    RnacentralDatabases("lncbook", "LncBook", 572.57),
    RnacentralDatabases("lncipedia", "LNCipedia", 194.81),
    RnacentralDatabases("lncrnadb", "lncRNAdb", 0.19),
    RnacentralDatabases("malacards", "MalaCards", 111.47),
    RnacentralDatabases("mgi", "MGI", 14.60),
    RnacentralDatabases("mirbase", "miRBase", 4.657073),
    RnacentralDatabases("mirgenedb", "MirGeneDB", 1.27),
    RnacentralDatabases("modomics", "Modomics", 0.05),
    RnacentralDatabases("noncode", "NONCODE", 265.43),
    RnacentralDatabases("pdbe", "PDBe", 2.16),
    RnacentralDatabases("pirbase", "piRBase", 6.04),
    RnacentralDatabases("pombase", "PomBase", 6.46),
    RnacentralDatabases("rdp", "RDP", 9.36),
    RnacentralDatabases("refseq", "RefSeq", 83.68),
    RnacentralDatabases("rfam", "Rfam", 321.5),
    RnacentralDatabases("ribocentre", "Ribocentre", 21.86),
    RnacentralDatabases("rgd", "RGD", 26.12),
    RnacentralDatabases("sgd", "SGD", 0.07),
    RnacentralDatabases("silva", "SILVA", 8584.62),
    RnacentralDatabases("snodb", "snoDB", 0.27),
    RnacentralDatabases("snopy", "snOPY", 0.29),
    RnacentralDatabases("snorna_database", "snoRNA Database", 0.03),
    RnacentralDatabases("srpdb", "SRPDB", 0.13),
    RnacentralDatabases("tair", "TAIR", 1.82),
    RnacentralDatabases("tarbase", "TarBase", 0.03),
    RnacentralDatabases("tmrna_web", "tmRNA Website", 35.38),
    RnacentralDatabases("wormbase", "WormBase", 4.53),
    RnacentralDatabases("zfin", "ZFIN", 0.97),
    RnacentralDatabases("zwd", "ZWD", 4.44)
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
