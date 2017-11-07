# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from future.utils import iteritems

import yaml
import json

from mlalchemy.errors import *
from mlalchemy.structures import *
from mlalchemy.constants import *
from mlalchemy.utils import *

import logging
logger = logging.getLogger(__name__)

__all__ = [
    "parse_yaml_query",
    "parse_json_query",
    "parse_query",
    "parse_query_fragment"
]


def parse_yaml_query(yaml_content):
    """Parses the given YAML string to attempt to extract a query.

    Args:
        yaml_content: A string containing YAML content.

    Returns:
        On success, the processed MLQuery object.
    """
    logger.debug("Attempting to parse YAML content:\n%s" % yaml_content)
    return parse_query(yaml.safe_load(yaml_content))


def parse_json_query(json_content):
    """Parses the given JSON string to attempt to extract a query.

    Args:
        json_content: A string containing JSON content.

    Returns:
        On success, the processed MLQuery object.
    """
    logger.debug("Attempting to parse JSON content:\n%s" % json_content)
    return parse_query(json.loads(json_content))


def parse_query(qd):
    """Parses the given query dictionary to produce an MLQuery object.

    Args:
        qd: A Python dictionary (pre-parsed from JSON/YAML) from which to extract the query.

    Returns:
        On success, the processed MLQuery object.
    """
    if not isinstance(qd, dict):
        raise TypeError("Argument for query parsing must be a Python dictionary")
    if 'from' not in qd:
        raise QuerySyntaxError("Missing \"from\" argument in query")

    logger.debug("Attempting to parse query dictionary:\n%s" % json_dumps(qd, indent=2))

    qf = parse_query_fragment(qd['where']).simplify() if 'where' in qd else None
    if isinstance(qf, MLClause):
        qf = MLQueryFragment(OP_AND, clauses=[qf])

    return MLQuery(
        qd['from'],
        query_fragment=qf,
        order_by=qd.get('orderBy', qd.get('order-by', qd.get('order_by', None))),
        offset=qd.get('offset', None),
        limit=qd.get('limit', None)
    )


def parse_query_fragment(q, op=OP_AND, comp=COMP_EQ):
    """Parses the given query object for its query fragment only."""
    if not isinstance(q, list) and not isinstance(q, dict):
        raise TypeError("\"Where\" clause in query fragment must either be a list or a dictionary")

    # ensure we're always dealing with a list
    if not isinstance(q, list):
        q = [q]

    clauses = []
    sub_fragments = []

    for sub_q in q:
        if not isinstance(sub_q, dict):
            raise TypeError("Sub-fragment must be a dictionary: %s" % sub_q)

        for k, v in iteritems(sub_q):
            # if v is a sub-fragment with a specific operator
            if k in OPERATORS:
                s = parse_query_fragment(v, op=k, comp=comp).simplify()
            elif k in COMPARATORS:
                # it's a sub-fragment, but its comparator is explicitly specified
                s = parse_query_fragment(v, op=op, comp=k).simplify()
            else:
                # it must be a clause
                s = MLClause(k, comp, v)

            if isinstance(s, MLQueryFragment):
                sub_fragments.append(s)
            elif isinstance(s, MLClause):
                clauses.append(s)

    return MLQueryFragment(op, clauses=clauses, sub_fragments=sub_fragments)
