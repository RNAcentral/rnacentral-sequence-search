import unittest

from sequence_search.consumer.rnacentral_databases import producer_to_consumers_databases


class TestProducerToConsumersDatabases(unittest.TestCase):

    def test_producer_to_consumers_databases_ena(self):
        assert producer_to_consumers_databases(['mirbase', 'refseq']) == [
            'mirbase-0.fasta',
            'refseq-0.fasta'
        ]

    def test_producer_to_consumers_databases_empty(self):
        assert producer_to_consumers_databases([]) == [
            'all-except-rrna-14.fasta', 'whitelist-rrna.part_005.fasta', 'all-except-rrna-5.fasta',
            'all-except-rrna-7.fasta', 'whitelist-rrna.part_007.fasta', 'all-except-rrna-16.fasta',
            'whitelist-rrna.part_003.fasta', 'all-except-rrna-12.fasta', 'all-except-rrna-3.fasta',
            'all-except-rrna-1.fasta', 'all-except-rrna-10.fasta', 'whitelist-rrna.part_001.fasta',
            'all-except-rrna-6.fasta', 'all-except-rrna-17.fasta', 'whitelist-rrna.part_006.fasta',
            'whitelist-rrna.part_004.fasta', 'all-except-rrna-15.fasta', 'all-except-rrna-4.fasta',
            'all-except-rrna-0.fasta', 'all-except-rrna-11.fasta', 'all-except-rrna-13.fasta',
            'whitelist-rrna.part_002.fasta', 'all-except-rrna-2.fasta', 'all-except-rrna-8.fasta',
            'all-except-rrna-19.fasta', 'whitelist-rrna.part_008.fasta', 'whitelist-rrna.part_010.fasta',
            'all-except-rrna-9.fasta', 'whitelist-rrna.part_009.fasta', 'all-except-rrna-18.fasta'
        ]
