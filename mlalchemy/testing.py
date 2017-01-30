# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import unittest

from mlalchemy.structures import *

__all__ = [
    "MLAlchemyTestCase"
]


class MLAlchemyTestCase(unittest.TestCase):
    """Helper class to speed up the writing of relatively complex unit tests."""

    def assertQueryEquals(self, src, q):
        self.assertIsInstance(q, MLQuery)
        self.assertEqual(src.table, q.table)
        self.assertQueryFragmentEquals(src.query_fragment, q.query_fragment)
        self.assertEqual(src.order_by, q.order_by)
        self.assertEqual(src.offset, q.offset)
        self.assertEqual(src.limit, q.limit)

    def assertQueryFragmentEquals(self, src, qf):
        self.assertIsInstance(qf, MLQueryFragment)
        self.assertEqual(src.op, qf.op)
        self.assertEqual(len(src.clauses), len(qf.clauses))
        self.assertEqual(len(src.sub_fragments), len(qf.sub_fragments))

        for i in range(len(src.clauses)):
            self.assertClauseEquals(
                src.clauses[i],
                qf.clauses[i]
            )

        for i in range(len(src.sub_fragments)):
            self.assertQueryFragmentEquals(
                src.sub_fragments[i],
                qf.sub_fragments[i]
            )

    def assertClauseEquals(self, src, clause):
        self.assertIsInstance(clause, MLClause)
        self.assertEqual(src.field, clause.field)
        self.assertEqual(src.comp, clause.comp)
        self.assertEqual(src.value, clause.value)
