# -*- coding: utf-8 -*-
"""Cache invalidation tests."""

# Standard Library
from unittest import TestCase

# Local
from ..invalidate import CacheHandler

try:
    from unittest import mock
except ImportError:
    import mock


class CacheHandlerTest(TestCase):

    """Abstract Test for CacheHandler."""

    def setUp(self):
        """Test set up."""
        self.handler = CacheHandler([])
        assert self.handler._caches == []
        for i in range(3):
            self.handler._caches.append(mock.Mock())

    def test_invalidate_page(self):
        """Ensure that all caches are invalidated."""
        self.handler.invalidate_page('http://acme.co.uk', '/')
        for cache in self.handler._caches:
            cache.invalidate_page.assert_called_once_with('http://acme.co.uk', '/', False)

    def test_invalidate_path(self):
        """Ensure that all caches are invalidated."""
        self.handler.invalidate_path('http://acme.co.uk', '/')
        for cache in self.handler._caches:
            cache.invalidate_path.assert_called_once_with('http://acme.co.uk', '/', False)


class VarnishTest(TestCase):

    """Test the varnish implementation."""

    def setUp(self):
        """Test set up."""
        caches = [{'BACKEND': 'varnish',
                   'LOCATION': 'http://localhost:6081'},
                  {'BACKEND': 'varnish',
                   'LOCATION': 'http://proxy2:6081'},
                  ]
        self.handler = CacheHandler(caches)

    @mock.patch('requests.request')
    def test_invalidate_page(self, mock_request):
        """Ensure that all caches are invalidated."""
        self.handler.invalidate_page('http://acme.co.uk', '/')
        assert mock_request.call_count == 2

    @mock.patch('requests.request')
    def test_invalidate_path(self, mock_request):
        """Ensure that all caches are invalidated."""
        self.handler.invalidate_path('http://acme.co.uk', '/')
        assert mock_request.call_count == 2
