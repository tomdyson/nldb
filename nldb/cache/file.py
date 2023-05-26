import json
import time
from pathlib import Path
from typing import Optional

from .base import CacheBackend


class FileCache(CacheBackend):
    def __init__(
        self, cache_dir: Optional[str] = "cache", ttl: Optional[int] = None
    ) -> None:
        self.cache_dir = Path(cache_dir)
        self.ttl = ttl

        # ensure the cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def _is_cache_expired(self, cache_path: Path) -> bool:
        """
        Checks whether a given cache file is expired.
        """
        if not self.ttl:
            # if ttl is not set, cache never expires
            return False

        modified_time = cache_path.stat().st_mtime
        current_time = time.time()
        return current_time - modified_time > self.ttl

    def get(self, key: str) -> Optional[bytes]:
        """
        Returns the cached value for the given key, if it exists and is not expired.
        """
        cache_path = self._get_cache_path(key)
        if cache_path.is_file() and not self._is_cache_expired(cache_path):
            return json.loads(cache_path.read_text())
        return None

    def set(self, key: str, value: bytes, ttl: Optional[int] = None) -> None:
        cache_path = self._get_cache_path(key)
        cache_path.write_text(str(value))

    def clear(self, key: Optional[str] = None) -> None:
        """
        Clears the cache.
        If key is specified, only the cached file for that key is cleared.
        """
        if key:
            if (cache_path := self._get_cache_path(key)) and cache_path.is_file():
                cache_path.unlink()
        else:
            self.cache_dir.rmdir()
