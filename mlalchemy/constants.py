# -*- coding: utf-8 -*-

from __future__ import unicode_literals

__all__ = [
    "OP_AND",
    "OP_OR",
    "OP_NOT",
    "OPERATORS",
    "COMP_EQ",
    "COMP_GT",
    "COMP_GTE",
    "COMP_LT",
    "COMP_LTE",
    "COMP_NEQ",
    "COMP_LIKE",
    "COMP_IN",
    "COMP_NIN",
    "COMP_IS",
    "COMPARATORS",
    "ORDER_ASC",
    "ORDER_DESC",
    "QUERY_ORDERS"
]


# Supported logical SQL query operators
OP_AND = "$and"
OP_OR = "$or"
OP_NOT = "$not"
OPERATORS = {OP_AND, OP_OR, OP_NOT}

# Supported SQL query comparators
COMP_EQ = "$eq"
COMP_GT = "$gt"
COMP_GTE = "$gte"
COMP_LT = "$lt"
COMP_LTE = "$lte"
COMP_NEQ = "$neq"
COMP_LIKE = "$like"
COMP_IN = "$in"
COMP_NIN = "$nin"
COMP_IS = "$is"
COMPARATORS = {COMP_EQ, COMP_GT, COMP_GTE, COMP_LT, COMP_LTE, COMP_NEQ, COMP_LIKE, COMP_IN, COMP_NIN,
               COMP_IS}

ORDER_ASC = "asc"
ORDER_DESC = "desc"
QUERY_ORDERS = {ORDER_ASC, ORDER_DESC}
