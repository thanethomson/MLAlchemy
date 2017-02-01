# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from future.utils import iteritems

import os
import unittest
import logging

from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from datetime import date

from mlalchemy import parse_yaml_query, parse_json_query
from mlalchemy.constants import *

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    date_of_birth = Column(Date)
    children = Column(Integer)


YAML_QUERY_ALL_USERS = "from: User"
JSON_QUERY_ALL_USERS = """{"from": "User"}"""
YAML_QUERY_YOUNG_USERS = """from: User
where:
    $gt:
        date-of-birth: 1988-01-01
"""
JSON_QUERY_LASTNAME_MICHAEL = """{
    "from": "User",
    "where": {
        "$like": {
            "lastName": "Mich%"
        }
    }
}"""
YAML_LIMIT_QUERY = """from: User
limit: 2
"""

YAML_ORDERED_QUERY = """from: User
order-by: "-date-of-birth"
"""

YAML_COMPLEX_ORDERED_QUERY = """from: User
order-by:
    - last-name
    - "-date-of-birth"
"""

YAML_COMPARATOR_QUERIES = {
    COMP_EQ: ("from: User\n"
              "where:\n"
              "  first-name: Michael", {1,}),
    COMP_GT: ("from: User\n"
              "where:\n"
              "  $gt:\n"
              "    children: 2", {3,}),
    COMP_GTE: ("from: User\n"
               "where:\n"
               "  $gte:\n"
               "    children: 2", {2, 3, 4}),
    COMP_LT: ("from: User\n"
              "where:\n"
              "  $lt:\n"
              "    children: 2", {1,}),
    COMP_LTE: ("from: User\n"
               "where:\n"
               "  $lte:\n"
               "    children: 2", {1, 2, 4}),
    COMP_NEQ: ("from: User\n"
               "where:\n"
               "  $neq:\n"
               "    last-name: Michaels", {1,}),
    COMP_LIKE: ("from: User\n"
                "where:\n"
                "  $like:\n"
                "    first-name: Mich%", {1,}),
    COMP_IN: ("from: User\n"
              "where:\n"
              "  $in:\n"
              "    last-name:\n"
              "      - Anderson\n"
              "      - Michaels", {1, 2, 3}),
    COMP_NIN: ("from: User\n"
               "where:\n"
               "  $nin:\n"
               "    children:\n"
               "      - 2\n"
               "      - 3", {1,}),
    COMP_IS: ("from: User\n"
              "where:\n"
              "  $is:\n"
              "    last-name: null", {4,})
}


DEBUG_LOGGING = (os.environ.get("DEBUG", False) == "True")


class TestSqlAlchemyQuerying(unittest.TestCase):

    engine = None
    session = None
    tables = None
    data = None

    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", echo=DEBUG_LOGGING)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        # add some initial data
        user1 = User(first_name="Michael", last_name="Anderson", date_of_birth=date(1980, 1, 1), children=0)
        user2 = User(first_name="James", last_name="Michaels", date_of_birth=date(1976, 10, 23), children=2)
        user3 = User(first_name="Andrew", last_name="Michaels", date_of_birth=date(1988, 8, 12), children=3)
        self.session.add_all([user1, user2, user3])
        self.session.commit()

        self.tables = {
            "User": User
        }
        self.data = {
            "User": {
                user1.id: user1,
                user2.id: user2,
                user3.id: user3
            }
        }
        if DEBUG_LOGGING:
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s',
            )

    def tearDown(self):
        self.session.close()

    def test_all_comparators(self):
        user4 = User(first_name="Gary", last_name=None, date_of_birth=date(1985, 2, 3), children=2)
        self.session.add(user4)
        self.session.commit()
        for comp, crit in iteritems(YAML_COMPARATOR_QUERIES):
            qs, expected_ids = crit
            results = parse_yaml_query(qs).to_sqlalchemy(self.session, self.tables).all()
            seen_ids = set([result.id for result in results])
            self.assertEqual(expected_ids, seen_ids, "Failed with comparator: %s (expected %s, got %s)" % (
                comp, expected_ids, seen_ids
            ))

    def test_basic_querying(self):
        self.assertAllUsers(parse_yaml_query(YAML_QUERY_ALL_USERS))
        self.assertAllUsers(parse_json_query(JSON_QUERY_ALL_USERS))
        self.assertYoungUsers(parse_yaml_query(YAML_QUERY_YOUNG_USERS))
        self.assertMichaelsUsers(parse_json_query(JSON_QUERY_LASTNAME_MICHAEL))
        self.assertLimits(parse_yaml_query(YAML_LIMIT_QUERY))
        self.assertOrderedSimple(parse_yaml_query(YAML_ORDERED_QUERY))
        self.assertOrderedComplex(parse_yaml_query(YAML_COMPLEX_ORDERED_QUERY))

    def assertAllUsers(self, mlquery):
        seen_users = self.query_seen_users(mlquery)
        self.assertEqual(3, len(seen_users))
        for user_id, user in iteritems(self.data["User"]):
            self.assertIn(user_id, seen_users)

    def assertYoungUsers(self, mlquery):
        seen_users = self.query_seen_users(mlquery)
        self.assertEqual(1, len(seen_users))
        # ID 3
        self.assertIn(3, seen_users)

    def assertMichaelsUsers(self, mlquery):
        seen_users = self.query_seen_users(mlquery)
        self.assertEqual(2, len(seen_users))
        self.assertIn(2, seen_users)
        self.assertIn(3, seen_users)

    def assertLimits(self, mlquery):
        seen_users = self.query_seen_users(mlquery)
        self.assertEqual(2, len(seen_users))
        self.assertIn(1, seen_users)
        self.assertIn(2, seen_users)

    def assertOrderedSimple(self, mlquery):
        results = mlquery.to_sqlalchemy(self.session, self.tables).all()
        self.assertEqual(3, results[0].id)
        self.assertEqual(1, results[1].id)
        self.assertEqual(2, results[2].id)

    def assertOrderedComplex(self, mlquery):
        results = mlquery.to_sqlalchemy(self.session, self.tables).all()
        self.assertEqual(1, results[0].id)
        self.assertEqual(3, results[1].id)
        self.assertEqual(2, results[2].id)

    def query_seen_users(self, mlquery):
        results = mlquery.to_sqlalchemy(self.session, self.tables).all()
        seen_users = set()
        for result in results:
            seen_users.add(result.id)
        return seen_users


if __name__ == "__main__":
    unittest.main()
