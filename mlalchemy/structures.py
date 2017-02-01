# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from past.builtins import basestring

from sqlalchemy.sql.expression import and_, or_, not_
from sqlalchemy.orm.attributes import QueryableAttribute

from mlalchemy.constants import *
from mlalchemy.errors import *
from mlalchemy.utils import *

import logging
logger = logging.getLogger(__name__)

__all__ = [
    "MLQuery",
    "MLQueryFragment",
    "MLClause"
]


class MLQuery(object):
    """Broad data structure used to represent a selection query in its entirety."""

    def __init__(self, table, query_fragment=None, order_by=None, offset=None, limit=None):
        """Constructor.

        Args:
            table: The name of the table being queried.
            query_fragment: A single instance of MLQueryFragment that represents the top of the hierarchy of
                query fragments making up this query. This can be None (i.e. no query criteria; all entries of
                the specified table will be selected).
            order_by: A string or list indicating the name of the field by which to order results, including
                the direction of ordering. For example, if a field's name is "title", specifying order_by as
                "title" will sort by "title" in the *ascending* direction. Specifying "-title" will sort in the
                descending direction. This can also be an ordered list of field names/directions.
            offset: The number of entries to skip. Set to None if no offset is required.
            limit: The maximum number of entries to return. Set to None to specify no limit.
        """
        if not isinstance(table, basestring):
            raise TypeError("The table name supplied to an MLQuery object must be a string")
        if query_fragment is not None and not isinstance(query_fragment, MLQueryFragment):
            raise TypeError("Primary query fragment for MLQuery must be of type MLQueryFragment")
        if order_by is not None and not isinstance(order_by, basestring) and not isinstance(order_by, list):
            raise TypeError("Query ordering parameter must be a string or a list")

        self.unique_field_names = set()
        self.table = table
        self.query_fragment = query_fragment

        if self.query_fragment is not None:
            self.unique_field_names = self.unique_field_names.union(self.query_fragment.unique_field_names)

        self.order_by = []
        if order_by is not None:
            # make sure our order_by field is a list
            if not isinstance(order_by, list):
                order_by = [order_by]

            for ob in order_by:
                field_name = ob.strip("-")
                # make sure it's in snake_case
                if is_camelcase_string(field_name):
                    field_name = camelcase_to_snakecase(field_name)
                elif is_kebabcase_string(field_name):
                    field_name = kebabcase_to_snakecase(field_name)
                self.order_by.append({field_name: ORDER_DESC if ob[0] == "-" else ORDER_ASC})
                self.unique_field_names.add(field_name)

        self.offset = offset
        self.limit = limit

    def as_dict(self):
        return {
            "table": self.table,
            "query_fragment": self.query_fragment.as_dict() if self.query_fragment is not None else None,
            "order_by": self.order_by,
            "offset": self.offset,
            "limit": self.limit
        }

    def unpack(self):
        return self.table, self.query_fragment, self.order_by, self.offset, self.limit

    def __repr__(self):
        return json_dumps(self.as_dict(), indent=2)

    def to_sqlalchemy(self, session, tables):
        if not isinstance(tables, dict):
            raise TypeError("Supplied tables structure for MLQuery-to-SQLAlchemy query conversion must be a dictionary")
        if self.table not in tables:
            raise InvalidTableError("Table does not exist in tables dictionary: %s" % self.table)

        table = tables[self.table]
        query = session.query(table)

        logger.debug("Attempting to build SQLAlchemy query for table \"%s\":\n%s" % (self.table, self))

        if self.query_fragment is not None:
            query = query.filter(self.query_fragment.to_sqlalchemy(table))

        if self.order_by is not None:
            criteria = []
            for order_by in self.order_by:
                field, direction = [i for i in order_by.items()][0]
                criterion = getattr(table, field)
                if not isinstance(criterion, QueryableAttribute):
                    raise InvalidFieldError("Invalid field for specified table: %s" % field)

                if direction == ORDER_ASC:
                    criterion = criterion.asc()
                elif direction == ORDER_DESC:
                    criterion = criterion.desc()
                criteria.append(criterion)
            query = query.order_by(*criteria)

        if self.offset is not None:
            query = query.offset(self.offset)

        if self.limit is not None:
            query = query.limit(self.limit)

        return query


class MLQueryFragment(object):
    """Recursive object to allow for relatively complex data selection queries."""

    def __init__(self, op, clauses=None, sub_fragments=None):
        """Constructor.

        Args:
            op: The operator to join clauses and sub-queries.
            clauses: A list of clauses (MLClause objects) for the query. Set to None if there are none.
            sub_fragments: A list of sub-queries (MLQueryFragment objects) within this query. Set to None if there are
                none.
        """
        if op not in OPERATORS:
            raise InvalidOperatorError("Invalid operator: %s" % op)

        if clauses is not None and not isinstance(clauses, list):
            raise TypeError("MLQueryFragment clauses must either be None or a list")
        if sub_fragments is not None and not isinstance(sub_fragments, list):
            raise TypeError("MLQueryFragment sub-fragments must either be None or a list")

        # ensure an empty list if no clauses or sub-queries
        if clauses is None:
            clauses = []
        if sub_fragments is None:
            sub_fragments = []

        self.unique_field_names = set()

        for clause in clauses:
            if not isinstance(clause, MLClause):
                raise TypeError("All clauses within an MLQueryFragment must be of type MLClause")
            self.unique_field_names.add(clause.field)

        for sub_frag in sub_fragments:
            if not isinstance(sub_frag, MLQueryFragment):
                raise TypeError("All sub-fragments within an MLQueryFragment must be of type MLQueryFragment")

            self.unique_field_names = self.unique_field_names.union(sub_frag.unique_field_names)

        if op == OP_NOT and (len(clauses) + len(sub_fragments)) > 1:
            raise QuerySyntaxError("NOT operations can only contain a single clause or sub-query fragment")

        self.op = op
        self.clauses = clauses
        self.sub_fragments = sub_fragments

    def unpack(self):
        return self.op, self.clauses, self.sub_fragments

    def as_dict(self):
        return {
            "op": self.op,
            "clauses": [clause.as_dict() for clause in self.clauses],
            "sub_fragments": [sub_fragment.as_dict() for sub_fragment in self.sub_fragments]
        }

    def __repr__(self):
        return json_dumps(self.as_dict(), indent=2)

    def simplify(self):
        op = self.op
        clauses = [clause for clause in self.clauses]
        sub_fragments = []

        for sub_fragment in self.sub_fragments:
            s = sub_fragment.simplify()
            if isinstance(s, MLClause):
                clauses.append(s)
            elif isinstance(s, MLQueryFragment):
                sub_fragments.append(s)

        # if this query fragment is only made up of a single clause
        if len(clauses) == 1 and len(sub_fragments) == 0 and op == OP_AND:
            return clauses[0]

        # if this query fragment is just a single sub-fragment, collapse its properties into the simplified
        # fragment we're currently generating
        if len(clauses) == 0 and len(sub_fragments) == 1:
            op, clauses, sub_fragments = sub_fragments[0].unpack()

        return MLQueryFragment(op, clauses=clauses, sub_fragments=sub_fragments)

    def to_sqlalchemy(self, table):
        filter_criteria = [clause.to_sqlalchemy(table) for clause in self.clauses]
        filter_criteria.extend([sub_frag.to_sqlalchemy(table) for sub_frag in self.sub_fragments])

        if self.op == OP_OR:
            return or_(*filter_criteria)
        elif self.op == OP_NOT:
            return not_(*filter_criteria)

        return and_(*filter_criteria)


class MLClause(object):
    """A single clause in an MLQuery object."""

    def __init__(self, field, comp, value):
        """Constructor.

        Args:
            field: The name of the field relevant to this clause.
            comp: The comparator when performing the comparison.
            value: The value to which this field's value is being compared.
        """
        if comp not in COMPARATORS:
            raise InvalidComparatorError("Invalid comparator: %s" % comp)

        if not isinstance(field, basestring):
            raise TypeError("Clause field names must be strings")

        # ensure field name is in snake_case
        if is_kebabcase_string(field):
            field = kebabcase_to_snakecase(field)
        elif is_camelcase_string(field):
            field = camelcase_to_snakecase(field)

        self.field = field
        self.comp = comp
        self.value = value

    def as_dict(self):
        return {
            "field": self.field,
            "comp": self.comp,
            "value": self.value
        }

    def unpack(self):
        return self.field, self.comp, self.value

    def __repr__(self):
        return json_dumps(self.as_dict(), indent=2)

    def to_sqlalchemy(self, table):
        col = getattr(table, self.field)
        # make sure it's the right kind of field
        if not isinstance(col, QueryableAttribute):
            raise InvalidFieldError("Invalid field for specified table: %s" % self.field)

        if self.comp == COMP_EQ:
            return col == self.value
        elif self.comp == COMP_GT:
            return col > self.value
        elif self.comp == COMP_GTE:
            return col >= self.value
        elif self.comp == COMP_LT:
            return col < self.value
        elif self.comp == COMP_LTE:
            return col <= self.value
        elif self.comp == COMP_NEQ:
            return col != self.value
        elif self.comp == COMP_LIKE:
            return col.like(self.value)
        elif self.comp == COMP_IN:
            return col.in_(self.value)
        elif self.comp == COMP_NIN:
            return ~col.in_(self.value)
        elif self.comp == COMP_IS:
            return col.is_(self.value)

        # default to equals
        return col == self.value
