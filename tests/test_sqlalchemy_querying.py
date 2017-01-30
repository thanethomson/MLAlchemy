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

    def test_basic_querying(self):
        self.assertAllUsers(parse_yaml_query(YAML_QUERY_ALL_USERS))
        self.assertAllUsers(parse_json_query(JSON_QUERY_ALL_USERS))
        self.assertYoungUsers(parse_yaml_query(YAML_QUERY_YOUNG_USERS))
        self.assertMichaelsUsers(parse_json_query(JSON_QUERY_LASTNAME_MICHAEL))
        self.assertLimits(parse_yaml_query(YAML_LIMIT_QUERY))

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

    def query_seen_users(self, mlquery):
        results = mlquery.to_sqlalchemy(self.session, self.tables).all()
        seen_users = set()
        for result in results:
            seen_users.add(result.id)
        return seen_users


if __name__ == "__main__":
    unittest.main()
