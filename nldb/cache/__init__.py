from nldb.config import get_settings

from .file import FileCache

settings = get_settings()

cache = FileCache(cache_dir=settings.cache_dir, ttl=settings.cache_ttl)
