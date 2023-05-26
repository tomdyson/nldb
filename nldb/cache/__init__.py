from functools import wraps
from typing import Optional

from .file import FileCache


def cache(cache_dir: Optional[str], ttl: int):
    def decorator(func):
        file_cache = FileCache(cache_dir=cache_dir, ttl=ttl)

        @wraps(func)
        async def wrapper(self, key: str, *args, **kwargs):
            if (value := file_cache.get(key)) is None:
                value = await func(self, *args, **kwargs)
                await file_cache.set(key, value, ttl=ttl)

            return value

        return wrapper

    return decorator
