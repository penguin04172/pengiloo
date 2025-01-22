import unittest
from unittest.mock import Mock

from fastapi import WebSocket

from .scoring_panel_register import ScoringPanelRegister


class TestScoringPanelRegister(unittest.TestCase):
    def test_register(self):
        registry = ScoringPanelRegister()
        self.assertEqual(0, registry.get_num_panels('red'))
        self.assertEqual(0, registry.get_num_score_commited('red'))
        self.assertEqual(0, registry.get_num_panels('blue'))
        self.assertEqual(0, registry.get_num_score_commited('blue'))

        panel1 = Mock(spec=WebSocket)
        panel2 = Mock(spec=WebSocket)
        panel3 = Mock(spec=WebSocket)

        registry.register_panel('red', panel1)
        registry.register_panel('blue', panel2)
        registry.register_panel('red', panel3)

        self.assertEqual(2, registry.get_num_panels('red'))
        self.assertEqual(0, registry.get_num_score_commited('red'))
        self.assertEqual(1, registry.get_num_panels('blue'))
        self.assertEqual(0, registry.get_num_score_commited('blue'))

        registry.set_score_commited('red', panel3)
        registry.set_score_commited('blue', panel2)
        registry.set_score_commited('blue', panel2)
        self.assertEqual(2, registry.get_num_panels('red'))
        self.assertEqual(1, registry.get_num_score_commited('red'))
        self.assertEqual(1, registry.get_num_panels('blue'))
        self.assertEqual(1, registry.get_num_score_commited('blue'))

        registry.unregister_panel('red', panel1)
        registry.unregister_panel('blue', panel2)
        self.assertEqual(1, registry.get_num_panels('red'))
        self.assertEqual(1, registry.get_num_score_commited('red'))
        self.assertEqual(0, registry.get_num_panels('blue'))
        self.assertEqual(0, registry.get_num_score_commited('blue'))

        registry.reset_score_commited()
        self.assertEqual(1, registry.get_num_panels('red'))
        self.assertEqual(0, registry.get_num_score_commited('red'))
        self.assertEqual(0, registry.get_num_panels('blue'))
        self.assertEqual(0, registry.get_num_score_commited('blue'))
