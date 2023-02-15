import logging
import typing as t

import pymysql
import pymysql.cursors

from .base_wrapper import BaseWrapper
from .exceptions_ import (
    MySQLWrapperError,
    MySQLWrapperBehaviorError,
    MySQLWrapperTransactionError,
    MySQLWrapperContextError
)


log = logging.getLogger(__name__)


class PyMySQLWrapper(BaseWrapper[pymysql.cursors.Cursor]):
    def __init__(self, connection_params: dict, **kwargs):
        self._transactional = kwargs.pop("transactional", False)

        self._cursor_class = connection_params.pop(
            "cursorclass",  # noqa
            pymysql.cursors.DictCursor
        )
        self._connection_args = connection_params

        self._connection: t.Optional[pymysql.Connection] = None
        self._cursor: t.Optional[pymysql.cursors.Cursor] = None
        self._transaction_is_started = False

    def _ensure_connection_is_prepared(self):
        if self._connection:
            return

        raise MySQLWrapperBehaviorError("Connection isn't present")

    def connect(self) -> pymysql.cursors.Cursor:
        try:
            # by default autocommit=True always
            # transaction will start explicitly
            connection = pymysql.connect(
                **self._connection_args, autocommit=True
            )
            cursor = connection.cursor(self._cursor_class)

            self._connection, self._cursor = connection, cursor

        except pymysql.err.Error as ex:
            raise MySQLWrapperError("Can't create connection") from ex

        return self._cursor

    def close(self):
        for o in (self._cursor, self._connection):
            try:
                o.close()
            except (pymysql.err.Error, AttributeError) as ex:
                log.exception(ex)

        self._connection = self._cursor = None

    def begin(self):
        self._ensure_connection_is_prepared()

        try:
            self._connection.begin()
        except pymysql.err.Error as ex:
            raise MySQLWrapperTransactionError(
                "Can't start transaction"
            ) from ex

        self._transaction_is_started = True

    def commit(self):
        self._ensure_connection_is_prepared()

        if self._transaction_is_started:
            try:
                self._connection.commit()
            except pymysql.err.Error as ex:
                raise MySQLWrapperTransactionError(
                    "Can't commit transaction"
                ) from ex

            self._transaction_is_started = False

            return

        log.warning("Commit is called, but transaction isn't started")

    def rollback(self):
        self._ensure_connection_is_prepared()

        if self._transaction_is_started:
            try:
                self._connection.rollback()
            except pymysql.err.Error as ex:
                raise MySQLWrapperTransactionError(
                    "Can't rollback transaction"
                ) from ex

            self._transaction_is_started = False

            return

        log.warning("Rollback is called, but transaction isn't started")

    def __enter__(self) -> pymysql.cursors.Cursor:
        cursor = self.connect()

        if self._transactional:
            try:
                self.begin()
            except MySQLWrapperTransactionError as ex:
                log.exception(ex)
                self.close()
                raise

        return cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        have_an_exception = any([exc_type, exc_val, exc_tb])

        if self._transaction_is_started:
            finalizer = self._connection.commit

            if have_an_exception:
                finalizer = self._connection.rollback

            try:
                finalizer()
            except MySQLWrapperError as ex:
                log.exception(ex)

        if isinstance(exc_val, pymysql.err.Error):
            self.close()
            raise MySQLWrapperContextError("Exception inside wrapper context")

        super().__exit__(exc_type, exc_val, exc_tb)
