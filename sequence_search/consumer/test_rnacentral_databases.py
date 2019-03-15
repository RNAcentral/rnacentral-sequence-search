import unittest

from .rnacentral_databases import producer_to_consumers_databases


class TestProducerToConsumersDatabases(unittest.TestCase):
    """
    python3 -m unittest sequence_search.consumer.test_rnacentral_databases
    """
    def test_producer_to_consumers_databases_ena(self):
        assert producer_to_consumers_databases(['ena', 'refseq']) == [
            'ena1.fasta',
            'ena2.fasta',
            'ena3.fasta',
            'ena4.fasta',
            'ena5.fasta',
            'refseq.fasta'
        ]

    def test_producer_to_consumers_databases_empty(self):
        assert producer_to_consumers_databases([]) == [
            'all-except-rrna1.fasta',
            'all-except-rrna10.fasta',
            'all-except-rrna2.fasta',
            'all-except-rrna3.fasta',
            'all-except-rrna4.fasta',
            'all-except-rrna5.fasta',
            'all-except-rrna6.fasta',
            'all-except-rrna7.fasta',
            'all-except-rrna8.fasta',
            'all-except-rrna9.fasta',
            'whitelist-rrna1.fasta',
            'whitelist-rrna10.fasta',
            'whitelist-rrna2.fasta',
            'whitelist-rrna3.fasta',
            'whitelist-rrna4.fasta',
            'whitelist-rrna5.fasta',
            'whitelist-rrna6.fasta',
            'whitelist-rrna7.fasta',
            'whitelist-rrna8.fasta',
            'whitelist-rrna9.fasta'
        ]
