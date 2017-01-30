# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import unittest

from mlalchemy import *
from mlalchemy.testing import MLAlchemyTestCase


class TestComplexMLAlchemyParsing(MLAlchemyTestCase):

    def test_parse_complex_query1(self):
        query = parse_query({
            "from": "SomeTable",
            "where": [
                {
                    "$or": [
                        {"field1": 1},
                        {"field2": "something"}
                    ]
                },
                {
                    "$not": {"field3": "else"}
                },
                {
                    "$and": [
                        {
                            "$gt": {"field1": 5}
                        },
                        {
                            "$like": {"field3": "hello%"}
                        }
                    ]
                }
            ]
        })
        self.assertQueryEquals(
            MLQuery(
                table="SomeTable",
                query_fragment=MLQueryFragment(
                    OP_AND,
                    sub_fragments=[
                        MLQueryFragment(
                            OP_OR,
                            clauses=[
                                MLClause("field1", COMP_EQ, 1),
                                MLClause("field2", COMP_EQ, "something")
                            ]
                        ),
                        MLQueryFragment(
                            OP_NOT,
                            clauses=[MLClause("field3", COMP_EQ, "else")]
                        ),
                        MLQueryFragment(
                            OP_AND,
                            clauses=[
                                MLClause("field1", COMP_GT, 5),
                                MLClause("field3", COMP_LIKE, "hello%")
                            ]
                        )
                    ]
                )
            ),
            query
        )


if __name__ == "__main__":
    unittest.main()
