# -*- coding: utf-8 -*-

import unittest

from pybel import BELGraph
from pybel.constants import CITATION_REFERENCE, CITATION_TYPE, CITATION_TYPE_ONLINE, GMOD, INCREASES
from pybel.dsl import (
    abundance, activity, degradation, entity, gene, gmod, hgvs, pmod, protein, secretion,
    translocation,
)
from pybel.struct.filters.node_predicates import (
    has_activity, has_causal_in_edges, has_causal_out_edges,
    has_gene_modification, has_hgvs, has_protein_modification, has_variant, is_abundance, is_degraded, is_gene,
    is_pathology, is_protein, is_translocated, keep_node_permissive, node_exclusion_filter_builder, not_pathology,
)

p1 = protein(name='BRAF', namespace='HGNC')
p2 = protein(name='BRAF', namespace='HGNC', variants=[hgvs('p.Val600Glu'), pmod('Ph')])

g1 = gene(name='BRAF', namespace='HGNC', variants=[gmod('Me')])


class TestPredicate(unittest.TestCase):
    def test_none(self):
        g = BELGraph()
        p1_tuple = g.add_node_from_data(p1)
        self.assertTrue(keep_node_permissive(g, p1_tuple))

    def test_p1_data_variants(self):
        self.assertFalse(is_abundance(p1))
        self.assertFalse(is_gene(p1))
        self.assertTrue(is_protein(p1))
        self.assertFalse(is_pathology(p1))
        self.assertTrue(not_pathology(p1))

        self.assertFalse(has_variant(p1))
        self.assertFalse(has_protein_modification(p1))
        self.assertFalse(has_gene_modification(p1))
        self.assertFalse(has_hgvs(p1))

    def test_p1_tuple_variants(self):
        g = BELGraph()
        p1_tuple = g.add_node_from_data(p1)

        self.assertFalse(is_abundance(g, p1_tuple))
        self.assertFalse(is_gene(g, p1_tuple))
        self.assertTrue(is_protein(g, p1_tuple))
        self.assertFalse(is_pathology(g, p1_tuple))
        self.assertTrue(not_pathology(g, p1_tuple))

        self.assertFalse(has_variant(g, p1_tuple))
        self.assertFalse(has_protein_modification(g, p1_tuple))
        self.assertFalse(has_gene_modification(g, p1_tuple))
        self.assertFalse(has_hgvs(g, p1_tuple))

    def test_p2_data_variants(self):
        self.assertFalse(is_abundance(p2))
        self.assertFalse(is_gene(p2))
        self.assertTrue(is_protein(p2))
        self.assertFalse(is_pathology(p2))
        self.assertTrue(not_pathology(p2))

        self.assertTrue(has_variant(p2))
        self.assertFalse(has_gene_modification(p2))
        self.assertTrue(has_protein_modification(p2))
        self.assertTrue(has_hgvs(p2))

    def test_p2_tuple_variants(self):
        g = BELGraph()
        p2_tuple = g.add_node_from_data(p2)

        self.assertFalse(is_abundance(g, p2_tuple))
        self.assertFalse(is_gene(g, p2_tuple))
        self.assertTrue(is_protein(g, p2_tuple))
        self.assertFalse(is_pathology(g, p2_tuple))
        self.assertTrue(not_pathology(g, p2_tuple))

        self.assertTrue(has_variant(g, p2_tuple))
        self.assertFalse(has_gene_modification(g, p2_tuple))
        self.assertTrue(has_protein_modification(g, p2_tuple))
        self.assertTrue(has_hgvs(g, p2_tuple))

    def test_g1_variants(self):
        self.assertFalse(is_abundance(g1))
        self.assertTrue(is_gene(g1))
        self.assertFalse(is_protein(g1))
        self.assertFalse(is_pathology(g1))

        self.assertTrue(has_variant(g1))
        self.assertTrue(has_gene_modification(g1), msg='Should have {}: {}'.format(GMOD, g1))
        self.assertFalse(has_protein_modification(g1))
        self.assertFalse(has_hgvs(g1))

    def test_p1_active(self):
        """cat(p(HGNC:HSD11B1)) increases deg(a(CHEBI:cortisol))"""
        g = BELGraph()
        u = g.add_node_from_data(protein(name='HSD11B1', namespace='HGNC'))
        v = g.add_node_from_data(abundance(name='cortisol', namespace='CHEBI', identifier='17650'))

        g.add_qualified_edge(
            u,
            v,
            relation=INCREASES,
            citation={
                CITATION_TYPE: CITATION_TYPE_ONLINE, CITATION_REFERENCE: 'https://www.ncbi.nlm.nih.gov/gene/3290'
            },
            evidence="Entrez Gene Summary: Human: The protein encoded by this gene is a microsomal enzyme that catalyzes the conversion of the stress hormone cortisol to the inactive metabolite cortisone. In addition, the encoded protein can catalyze the reverse reaction, the conversion of cortisone to cortisol. Too much cortisol can lead to central obesity, and a particular variation in this gene has been associated with obesity and insulin resistance in children. Two transcript variants encoding the same protein have been found for this gene.",
            annotations={'Species': '9606'},
            subject_modifier=activity('cat'),
            object_modifier=degradation()
        )

        self.assertFalse(is_translocated(g, u))
        self.assertFalse(is_degraded(g, u))
        self.assertTrue(has_activity(g, u))

        self.assertFalse(is_translocated(g, v))
        self.assertTrue(is_degraded(g, v))
        self.assertFalse(has_activity(g, v))

    def test_object_has_translocation(self):
        """p(HGNC: EGF) increases tloc(p(HGNC: VCP), GOCCID: 0005634, GOCCID: 0005737)"""
        g = BELGraph()
        u = g.add_node_from_data(protein(name='EFG', namespace='HGNC'))
        v = g.add_node_from_data(protein(name='VCP', namespace='HGNC'))

        g.add_qualified_edge(
            u,
            v,
            relation=INCREASES,
            citation='10855792',
            evidence="Although found predominantly in the cytoplasm and, less abundantly, in the nucleus, VCP can be translocated from the nucleus after stimulation with epidermal growth factor.",
            annotations={'Species': '9606'},
            object_modifier=translocation(
                from_loc=entity(namespace='GO', identifier='0005634'),
                to_loc=entity(namespace='GO', identifier='0005737')
            )
        )

        self.assertFalse(is_translocated(g, u))
        self.assertFalse(is_degraded(g, u))
        self.assertFalse(has_activity(g, u))
        self.assertFalse(has_causal_in_edges(g, u))
        self.assertTrue(has_causal_out_edges(g, u))

        self.assertTrue(is_translocated(g, v))
        self.assertFalse(is_degraded(g, v))
        self.assertFalse(has_activity(g, v))
        self.assertTrue(has_causal_in_edges(g, v))
        self.assertFalse(has_causal_out_edges(g, v))

    def test_object_has_secretion(self):
        """p(MGI:Il4) increases sec(p(MGI:Cxcl1))"""
        g = BELGraph()
        u = g.add_node_from_data(protein(name='Il4', namespace='MGI'))
        v = g.add_node_from_data(protein(name='Cxcl1', namespace='MGI'))

        g.add_qualified_edge(
            u,
            v,
            relation=INCREASES,
            citation='10072486',
            evidence='Compared with controls treated with culture medium alone, IL-4 and IL-5 induced significantly higher levels of MIP-2 and KC production; IL-4 also increased the production of MCP-1 (Fig. 2, A and B)....we only tested the effects of IL-3, IL-4, IL-5, and IL-13 on chemokine expression and cellular infiltration....Recombinant cytokines were used, ... to treat naive BALB/c mice.',
            annotations={'Species': '10090', 'MeSH': 'bronchoalveolar lavage fluid'},
            object_modifier=secretion()
        )

        self.assertFalse(is_translocated(g, u))
        self.assertFalse(is_degraded(g, u))
        self.assertFalse(has_activity(g, u))
        self.assertFalse(has_causal_in_edges(g, u))
        self.assertTrue(has_causal_out_edges(g, u))

        self.assertTrue(is_translocated(g, v))
        self.assertFalse(is_degraded(g, v))
        self.assertFalse(has_activity(g, v))
        self.assertTrue(has_causal_in_edges(g, v))
        self.assertFalse(has_causal_out_edges(g, v))

    def test_subject_has_secretion(self):
        """sec(p(MGI:S100b)) increases a(CHEBI:"nitric oxide")"""
        g = BELGraph()
        u = g.add_node_from_data(protein(name='S100b', namespace='MGI'))
        v = g.add_node_from_data(abundance(name='nitric oxide', namespace='CHEBI'))

        g.add_qualified_edge(
            u,
            v,
            relation=INCREASES,
            citation='11180510',
            evidence='S100B protein is also secreted by astrocytes and acts on these cells to stimulate nitric oxide secretion in an autocrine manner.',
            annotations={'Species': '10090', 'Cell': 'astrocyte'},
            subject_modifier=secretion()
        )

        self.assertTrue(is_translocated(g, u))
        self.assertFalse(is_degraded(g, u))
        self.assertFalse(has_activity(g, u))
        self.assertFalse(has_causal_in_edges(g, u))
        self.assertTrue(has_causal_out_edges(g, u))

        self.assertFalse(is_translocated(g, v))
        self.assertFalse(is_degraded(g, v))
        self.assertFalse(has_activity(g, v))
        self.assertTrue(has_causal_in_edges(g, v))
        self.assertFalse(has_causal_out_edges(g, v))

    def test_node_exclusion_data(self):
        g = BELGraph()

        u = protein(name='S100b', namespace='MGI')
        v = abundance(name='nitric oxide', namespace='CHEBI')
        w = abundance(name='cortisol', namespace='CHEBI', identifier='17650')

        g.add_node_from_data(u)
        g.add_node_from_data(v)
        g.add_node_from_data(w)

        f = node_exclusion_filter_builder([u])

        self.assertFalse(f(u))
        self.assertTrue(f(v))
        self.assertTrue(f(w))

        f = node_exclusion_filter_builder([u, v])

        self.assertFalse(f(u))
        self.assertFalse(f(v))
        self.assertTrue(f(w))

        f = node_exclusion_filter_builder([])

        self.assertTrue(f(u))
        self.assertTrue(f(v))
        self.assertTrue(f(w))

    def test_node_exclusion_tuples(self):
        g = BELGraph()
        u = g.add_node_from_data(protein(name='S100b', namespace='MGI'))
        v = g.add_node_from_data(abundance(name='nitric oxide', namespace='CHEBI'))
        w = g.add_node_from_data(abundance(name='cortisol', namespace='CHEBI', identifier='17650'))

        f = node_exclusion_filter_builder([u])

        self.assertFalse(f(g, u))
        self.assertTrue(f(g, v))
        self.assertTrue(f(g, w))

        f = node_exclusion_filter_builder([u, v])

        self.assertFalse(f(g, u))
        self.assertFalse(f(g, v))
        self.assertTrue(f(g, w))

        f = node_exclusion_filter_builder([])

        self.assertTrue(f(g, u))
        self.assertTrue(f(g, v))
        self.assertTrue(f(g, w))
