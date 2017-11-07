# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import unittest
import yaml

from mlalchemy import *
from mlalchemy.testing import MLAlchemyTestCase


class TestYamlSecurity(MLAlchemyTestCase):

    def test_basic_yaml_security(self):
        with self.assertRaises(yaml.constructor.ConstructorError):
            parse_yaml_query('!!python/object/apply:os.system ["echo Hello"]')


if __name__ == "__main__":
    unittest.main()

