# -*- coding: utf-8 -*-
"""Cache invalidation base tests."""

# Standard Library
from unittest import TestCase

# Local
from ...backends.base import CacheInvalidationHandler


class CacheInvalidationHandlerTest(TestCase):
    """Test the Base Cache Handler."""

    def test_init_requires_valid_location(self):
        """Allow only valid http(s) urls as a location."""
        CacheInvalidationHandler("http://localhost")
        CacheInvalidationHandler("http://localhost:6081")
        CacheInvalidationHandler("https://localhost")
        with self.assertRaises(AssertionError):
            CacheInvalidationHandler("https://localhost/")
        with self.assertRaises(AssertionError):
            CacheInvalidationHandler("ftp://localhost")
        with self.assertRaises(AssertionError):
            CacheInvalidationHandler("localhost")
        with self.assertRaises(AssertionError):
            CacheInvalidationHandler("https://localhost/some-path")
        with self.assertRaises(AssertionError):
            CacheInvalidationHandler("https://localhost?q=some-path")
        with self.assertRaises(AssertionError):
            CacheInvalidationHandler("https://localhost#some-path")

    def test_invalidate_page_is_not_implemented(self):
        """Page invalidation is not implemented in the base class."""
        handler = CacheInvalidationHandler("http://localhost")
        with self.assertRaises(NotImplementedError):
            handler.invalidate_page(None, None)

    def test_inalidate_path_is_not_implemented(self):
        """Path invalidation is not implemented in the base class."""
        handler = CacheInvalidationHandler("http://localhost")
        with self.assertRaises(NotImplementedError):
            handler.invalidate_path(None, None)
