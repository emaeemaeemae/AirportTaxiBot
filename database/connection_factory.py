import typing as t

from .base_wrapper import BaseWrapper


CW = t.TypeVar("CW", bound=BaseWrapper)


class ConnectionFactory(t.Generic[CW]):
    def __init__(self,
                 connection_wrapper: t.Type[CW],
                 connection_params: dict = None):
        self._connection_wrapper = connection_wrapper
        self._connection_params = connection_params or {}

    def __call__(self, transactional: bool = False) -> CW:
        return self._connection_wrapper(
            self._connection_params,
            transactional=transactional
        )
