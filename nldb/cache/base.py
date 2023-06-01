from typing import Protocol, TypeVar, runtime_checkable

T = TypeVar("T", bound="CacheBackend")


@runtime_checkable
class CacheBackend(Protocol):
    def get(self: T, key: str) -> bytes | None:
        ...

    def set(self: T, key: str, value: bytes, ttl: int | None = None) -> None:
        ...

    def clear(self: T, key: str | None = None) -> None:
        ...
