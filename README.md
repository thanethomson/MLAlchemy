# MLAlchemy

[![Build Status](https://travis-ci.org/thanethomson/MLAlchemy.svg?branch=master)](https://travis-ci.org/thanethomson/MLAlchemy)
[![PyPI](https://img.shields.io/pypi/v/mlalchemy.svg)](https://pypi.python.org/pypi/mlalchemy)
[![PyPI](https://img.shields.io/pypi/pyversions/mlalchemy.svg)](https://pypi.python.org/pypi/mlalchemy)

## Overview
MLAlchemy is a Python-based utility library aimed at allowing relatively safe
conversion from YAML/JSON to SQLAlchemy read-only queries. One use case here is
to allow RESTful web applications (written in Python) to receive YAML- or
JSON-based queries for data, e.g. from a front-end JavaScript-based application.

The name "MLAlchemy" is an abbreviation for "Markup Language for
SQLAlchemy".

## Installation
Installation via PyPI:

```bash
> pip install mlalchemy
```

## Usage
A simple example of how to use MLAlchemy:

```python
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from mlalchemy import parse_yaml_query, parse_json_query

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    date_of_birth = Column(Date)


# use an in-memory SQLite database for this example
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# add a couple of dummy users
user1 = User(first_name="Michael", last_name="Anderson", date_of_birth=date(1980, 1, 1))
user2 = User(first_name="James", last_name="Michaels", date_of_birth=date(1976, 10, 23))
user3 = User(first_name="Andrew", last_name="Michaels", date_of_birth=date(1988, 8, 12))
session.add_all([user1, user2, user3])
session.commit()

# we need a lookup table for MLAlchemy
tables = {
    "User": User
}

# try a simple YAML-based query first
all_users = parse_yaml_query("from: User").to_sqlalchemy(session, tables).all()
print(all_users)

# same query, but this time in JSON
all_users = parse_json_query("""{"from": "User"}""").to_sqlalchemy(session, tables).all()
print(all_users)

# a slightly more complex query
young_users = parse_yaml_query("""from: User
where:
    $gt:
        date-of-birth: 1988-01-01
""").to_sqlalchemy(session, tables).all()
print(young_users)
```

## Query Language Syntax
As mentioned before, queries can either be supplied in YAML format or
in JSON format to one of the respective parsers.

#### `from`
At present, MLAlchemy can only support selecting data from a single
table (multi-table support is planned in future). Here, the `from`
parameter allows you to specify the name of the table from which
to select data.

#### `where`
The `where` parameter defines, in hierarchical fashion, the structure
of the logical query to perform. There are 3 kinds of key types in
the JSON/YAML structures, as described in the following table.

| Kind            | Description                                           | Options                                              |
| --------------- | ----------------------------------------------------- | ---------------------------------------------------- |
| **Operators**   | Logical (boolean) operators for combining sub-clauses | `$and`, `$or`, `$not`                                |
| **Comparators** | Comparative operators for comparing fields to values  | `$eq`, `$gt`, `$gte`, `$lt`, `$lte`, `$like`, `$neq` |
| **Field Names** | The name of a field in the `from` table               | (Depends on table)                                   |

#### `order-by` (YAML) or `orderBy` (JSON)
Provides the ordering for the resulting query. Must either be a single
field name or a list of field names, with the direction specifier in
front of the field name. For example:

```yaml
# Order by "field2" in ascending order
order-by: field2
```

Another example:

```yaml
# Order by "field2" in *descending* order
order-by: "-field2"
```

A more complex example:

```yaml
# Order first by "field1" in ascending order, then by "field2" in
# descending order
order-by:
    - field1
    - "-field2"
```

#### `offset`
Specifies the number of results to skip before providing results. If
not specified, no results are skipped.

#### `limit`
Specifies the maximum number of results to return. If not specified,
there will be no limit to the number of returned results.

#### Example 1
The following is an example of a relatively simple query in YAML format:

```yaml
from: SomeTable
where:
    - $gt:
        field1: 5
    - $lt:
        field2: 3
order-by:
    - field1
offset: 2
limit: 10
```

This would translate into the following SQLAlchemy query:

```python
from sqlalchemy.sql.expression import and_

session.query(SomeTable).filter(
    and_(SomeTable.field1 > 5, SomeTable.field2 < 3)
) \
    .order_by(SomeTable.field1) \
    .offset(2) \
    .limit(10)
```

#### Example 2
The following is an example of a more complex query in YAML format:

```yaml
from: SomeTable
where:
    - $or:
        field1: 5
        field2: something
    - $not:
        $like:
            field3: "else%"
```

This would translate into the following SQLAlchemy query:

```python
from sqlalchemy.sql.expression import and_, or_, not_

session.query(SomeTable) \
    .filter(
        and_(
            or_(
                SomeTable.field1 == 5,
                SomeTable.field2 == "something"
            ),
            not_(
                SomeTable.field3.like("else%")
            )
        )
    )
```

## License
**The MIT License (MIT)**

Copyright (c) 2017 Thane Thomson

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

