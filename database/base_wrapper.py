import abc
import typing as t


CursorType = t.TypeVar("CursorType")


class BaseWrapper(t.Generic[CursorType], abc.ABC):
    @abc.abstractmethod
    def connect(self) -> CursorType:
        ...

    @abc.abstractmethod
    def close(self):
        ...

    @abc.abstractmethod
    def begin(self):
        ...

    @abc.abstractmethod
    def commit(self):
        ...

    @abc.abstractmethod
    def rollback(self):
        ...

    @abc.abstractmethod
    def __enter__(self) -> CursorType:
        ...

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
