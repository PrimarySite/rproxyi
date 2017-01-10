# -*- coding: utf-8 -*-
"""Cache invalidation."""
# Standard Library
import warnings

# Local
from .backends.varnish import VarnishCache


class CacheHandler(object):

    """Base class to handle cache invalidation."""

    def __init__(self, cacheconfig):
        """
        Initialise a cache.

        cacheconfig is a list of dictionaries e.g.:
        [
            {'BACKEND': 'varnish', 'LOCATION': 'http://localhost:6081'},
        ]
        """
        self._caches = []
        for cache in cacheconfig:
            if cache['BACKEND'] == 'varnish':
                self._caches.append(VarnishCache(cache['LOCATION']))
        if not self._caches:
            warnings.warn('No caches set up - caching disabled')

    def invalidate_page(self, domain, path, purge=False):
        """
        Invalidate a single page.

        If purge is true then the page gets evicted from the cache immediately.
        """
        for cache in self._caches:
            cache.invalidate_page(domain, path, purge)

    def invalidate_path(self, domain, path, purge=False):
        """
        Invalidate an entire path.

        The path can contain a regular expression to be invalidated.
        If purge is true then the page gets evicted from the cache immediately.
        """
        for cache in self._caches:
            cache.invalidate_path(domain, path, purge)
