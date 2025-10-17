# Copyright 2025 Marimo. All rights reserved.

from functools import lru_cache
from typing import Literal, Optional, Union

from sqlglot import exp, parse
from sqlglot.errors import ParseError

from marimo import _loggers
from marimo._dependencies.dependencies import DependencyManager
from marimo._sql.error_utils import log_sql_error

LOGGER = _loggers.marimo_logger()

# DCL: Data Control Language, usually associated with auth (GRANT and REVOKE)
# DML: Data Manipulation Language, usually associated with changing data (INSERT, UPDATE, and DELETE)
# DQL: Data Query Language, usually associated with reading data (SELECT)
# DDL: Data Definition Language, usually associated with creating/altering/dropping tables (CREATE, ALTER, and DROP)
SQL_TYPE = Literal["DDL", "DML", "DQL", "DCL"]
SQLGLOT_DIALECTS = Literal[
    "duckdb", "clickhouse", "mysql", "postgres", "sqlite"
]


def classify_sql_statement(
    sql_statement: str, dialect: Optional[SQLGLOT_DIALECTS] = None
) -> Union[SQL_TYPE, Literal["unknown"]]:
    """
    Identifies whether a SQL statement is a DDL, DML, or DQL statement.
    """
    DependencyManager.sqlglot.require(why="SQL parsing")

    normalized_sql = sql_statement.strip().lower()
    try:
        with _loggers.suppress_warnings_logs("sqlglot"):
            # Use memoized parser to avoid repeated parses of the same SQL/dialect
            expression_list = _parse_sql_cached(normalized_sql, dialect)
    except ParseError as e:
        log_sql_error(
            LOGGER.debug,
            message="Failed to parse SQL statement for classification.",
            exception=e,
            rule_code="MF005",
            node=None,
            sql_content=normalized_sql,
        )
        return "unknown"

    ddl_types = (exp.Create, exp.Drop, exp.Alter, exp.Attach, exp.Detach)
    dml_types = (exp.Insert, exp.Update, exp.Delete)

    for expression in expression_list:
        if expression is None:
            continue

        if expression.find(*ddl_types):
            return "DDL"
        elif expression.find(*dml_types):
            return "DML"
        else:
            return "DQL"

    return "unknown"


# LRU cache for SQL statement parsing/classification for given SQL/dialect.
@lru_cache(maxsize=256)
def _parse_sql_cached(sql_statement: str, dialect: Optional[str]) -> tuple:
    # The cache key is (sql_statement, dialect)
    # Assumes sql_statement is already stripped and lowered; dialect is string or None
    return parse(sql_statement, dialect=dialect)
