# -*- coding: utf-8 -*-
"""Cache invalidation."""
try:
    # Standard Library
    from urllib.parse import urlparse
except ImportError:
    # 3rd-party
    from urlparse import urlparse


class CacheInvalidationHandler(object):
    """Base class to handle cache invalidation."""

    def __init__(self, location):
        """
        Initialise a cache.

        Location is the fully qualified URL to contact the cache server.
        """
        parsed = urlparse(location)
        assert parsed.scheme in ["http", "https"]
        assert parsed.netloc
        assert not parsed.path
        assert not parsed.params
        assert not parsed.query
        assert not parsed.fragment
        self.location = location

    def invalidate_page(self, domain, path, purge=False):
        """
        Invalidate a single page.

        If purge is true then the page gets evicted from the cache immediately.
        """
        raise NotImplementedError("Must be implemented by subclass.")

    def invalidate_path(self, domain, path, purge=False):
        """
        Invalidate an entire path.

        The path can contain a regular expression to be invalidated.
        If purge is true then the page gets evicted from the cache immediately.
        """
        raise NotImplementedError("Must be implemented by subclass.")
