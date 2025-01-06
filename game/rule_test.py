import unittest

from .rule import *


class RuleTest(unittest.TestCase):
	def test_get_rule_by_id(self):
		self.assertIsNone(get_rule_by_id(0))
		self.assertEqual(rules[0], list(get_rule_by_id(1).model_dump().values()))
		self.assertEqual(rules[20], list(get_rule_by_id(21).model_dump().values()))
		self.assertIsNone(get_rule_by_id(1000))

	def test_get_all_rules(self):
		all_rules = get_all_rules()
		self.assertEqual(len(rules), len(all_rules))
		for rule in rules:
			self.assertEqual(rule, list(all_rules[rule[0]].model_dump().values()))
