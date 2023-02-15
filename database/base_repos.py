import typing as t

import pymysql.cursors


MySQLCursors = t.Union[pymysql.cursors.Cursor, pymysql.cursors.DictCursor]


class BaseMySQLRepo:
    def __init__(self, cursor: MySQLCursors):
        self._cursor = cursor
