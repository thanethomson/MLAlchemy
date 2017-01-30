# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import date, datetime
import json
import re

__all__ = [
    "is_camelcase_string",
    "is_kebabcase_string",
    "camelcase_to_snakecase",
    "kebabcase_to_snakecase",
    "json_date_serializer",
    "json_dumps"
]

KEBABCASE_DETECT_RE = re.compile(r"^(([a-z][a-z0-9]+)\-)*([a-z][a-z0-9]+)$")
KEBABCASE_REPLACE_RE = re.compile(r"([a-z]+)\-")

CAMELCASE_DETECT_RE = re.compile(r"^([a-zA-Z][a-z0-9]*)([A-Z][a-z0-9]*)*$")
CAMELCASE_FIRST_CAP_RE = re.compile(r"(.)([A-Z][a-z]+)")
CAMELCASE_ALL_CAP_RE = re.compile(r"([a-z0-9])([A-Z])")


def is_camelcase_string(s):
    """Checks whether or not the given string is supplied in camelCase."""
    return CAMELCASE_DETECT_RE.match(s) is not None


def is_kebabcase_string(s):
    """Checks whether the given string is supplied in skewer-case."""
    return KEBABCASE_DETECT_RE.match(s) is not None


def camelcase_to_snakecase(s):
    s1 = CAMELCASE_FIRST_CAP_RE.sub(r"\1_\2", s)
    return CAMELCASE_ALL_CAP_RE.sub(r"\1_\2", s1).lower()


def kebabcase_to_snakecase(s):
    return KEBABCASE_REPLACE_RE.sub(r"\1_", s)


def json_date_serializer(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError("Type not serializable")


def json_dumps(obj, indent=None):
    return json.dumps(obj, indent=indent, default=json_date_serializer)
