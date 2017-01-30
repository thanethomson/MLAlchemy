# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import unittest

from mlalchemy import *
from mlalchemy.testing import MLAlchemyTestCase


class TestBasicMLAlchemyParsing(MLAlchemyTestCase):

    def test_parse_basic_query1(self):
        query = parse_query({
            "from": "SomeTable",
            "where": {
                "field": "value"
            }
        })
        self.assertQueryEquals(
            MLQuery(
                "SomeTable",
                query_fragment=MLQueryFragment(
                    OP_AND,
                    clauses=[
                        MLClause(
                            "field",
                            COMP_EQ,
                            "value"
                        )
                    ]
                )
            ),
            query
        )

    def test_parse_basic_query2(self):
        query = parse_query({
            "from": "SomeTable",
            "where": [
                {"field1": "value"},
                {"field2": 1}
            ]
        })
        self.assertQueryEquals(
            MLQuery(
                "SomeTable",
                query_fragment=MLQueryFragment(
                    OP_AND,
                    clauses=[
                        MLClause(
                            "field1",
                            COMP_EQ,
                            "value"
                        ),
                        MLClause(
                            "field2",
                            COMP_EQ,
                            1
                        )
                    ]
                )
            ),
            query
        )

    def test_parse_basic_query3(self):
        query = parse_query({
            "from": "SomeTable",
            "where": {
                "$or": [
                    {"field1": "value"},
                    {"field2": 1}
                ]
            }
        })
        self.assertQueryEquals(
            MLQuery(
                "SomeTable",
                query_fragment=MLQueryFragment(
                    OP_OR,
                    clauses=[
                        MLClause(
                            "field1",
                            COMP_EQ,
                            "value"
                        ),
                        MLClause(
                            "field2",
                            COMP_EQ,
                            1
                        )
                    ]
                )
            ),
            query
        )

    def test_parse_basic_query4(self):
        query = parse_query({
            "from": "SomeTable",
            "where": [
                {
                    "$not": {
                        "field1": 1
                    }
                }
            ],
            "orderBy": "field1",
            "offset": 10,
            "limit": 50
        })
        self.assertQueryEquals(
            MLQuery(
                "SomeTable",
                query_fragment=MLQueryFragment(
                    OP_NOT,
                    clauses=[
                        MLClause("field1", COMP_EQ, 1)
                    ]
                ),
                order_by=["field1"],
                offset=10,
                limit=50
            ),
            query
        )

    def test_parse_basic_query5(self):
        query = parse_query({
            "from": "SomeTable",
            "where": {
                "$gt": {
                    "field1": 5
                }
            }
        })
        self.assertQueryEquals(
            MLQuery(
                "SomeTable",
                query_fragment=MLQueryFragment(
                    OP_AND,
                    clauses=[
                        MLClause("field1", COMP_GT, 5)
                    ]
                )
            ),
            query
        )

    def test_parse_basic_query6(self):
        query = parse_query({
            "from": "SomeTable",
            "where": [
                {
                    "$gt": {
                        "field1": 5
                    }
                },
                {
                    "$lt": {
                        "field2": 10
                    }
                }
            ]
        })
        self.assertQueryEquals(
            MLQuery(
                "SomeTable",
                query_fragment=MLQueryFragment(
                    OP_AND,
                    clauses=[
                        MLClause("field1", COMP_GT, 5),
                        MLClause("field2", COMP_LT, 10)
                    ]
                )
            ),
            query
        )

    def test_parse_basic_query7(self):
        query = parse_query({
            "from": "SomeTable",
            "where": {"field1": 1},
            "orderBy": "-field1"
        })
        self.assertQueryEquals(
            MLQuery(
                "SomeTable",
                query_fragment=MLQueryFragment(
                    OP_AND,
                    clauses=[
                        MLClause("field1", COMP_EQ, 1)
                    ]
                ),
                order_by=["-field1"]
            ),
            query
        )

    def test_parse_basic_query8(self):
        query = parse_query({
            "from": "SomeTable",
            "where": {"field1": 1},
            "orderBy": ["-field1", "field2", "-field3"]
        })
        self.assertQueryEquals(
            MLQuery(
                "SomeTable",
                query_fragment=MLQueryFragment(
                    OP_AND,
                    clauses=[
                        MLClause("field1", COMP_EQ, 1)
                    ]
                ),
                order_by=["-field1", "field2", "-field3"]
            ),
            query
        )

    def test_parse_invalid_basic_queries(self):
        with self.assertRaises(TypeError):
            parse_query([])
        with self.assertRaises(QuerySyntaxError):
            parse_query(dict())

    def test_parse_invalid_basic_not_op(self):
        with self.assertRaises(QuerySyntaxError):
            parse_query({
                "from": "SomeTable",
                "where": {
                    "$not": [
                        {"field1": 1},
                        {"field2": 2}
                    ]
                }
            })

    def test_parse_invalid_field_name(self):
        with self.assertRaises(TypeError):
            parse_query({
                "from": "SomeTable",
                "where": {1: 1}
            })

    def test_parse_invalid_sub_fragment(self):
        with self.assertRaises(TypeError):
            parse_query({
                "from": "SomeTable",
                "where": 1
            })


if __name__ == "__main__":
    unittest.main()
