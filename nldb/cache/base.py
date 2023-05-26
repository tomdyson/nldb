from typing import Optional, Protocol, TypeVar, runtime_checkable

T = TypeVar("T", bound="CacheBackend")


@runtime_checkable
class CacheBackend(Protocol):
    def get(self: T, key: str) -> Optional[bytes]:
        ...

    def set(self: T, key: str, value: bytes, ttl: Optional[int] = None) -> None:
        ...

    def clear(self: T, key: Optional[str] = None) -> None:
        ...
