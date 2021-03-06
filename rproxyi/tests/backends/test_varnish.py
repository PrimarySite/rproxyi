# -*- coding: utf-8 -*-
"""Cache invalidation varnish tests."""
# Standard Library
from unittest import TestCase

# 3rd-party
import requests
from httmock import HTTMock
from httmock import all_requests
from httmock import response

# Local
from ...backends.varnish import VarnishCache

try:
    # Standard Library
    from unittest import mock
except ImportError:
    # 3rd-party
    import mock


@all_requests
def response_content(url, request):
    """Fake an error response for HTTMock."""
    return response(500, "FAIL", request=request)


class VarnishCacheTest(TestCase):
    """Test the varnish implementation of a CacheInvalidationHandler."""

    def setUp(self):
        """Test set up."""
        self.cache_url = "http://localhost:8080"
        self.handler = VarnishCache(self.cache_url)
        self.domain = "acme.co.uk"
        self.headers = {"host": self.domain}
        self.path = "/some/path"
        self.url = self.cache_url + self.path

    @mock.patch("requests.request")
    def test_request_accepts_purge_ban_only(self, mock_request):
        """Only PURGE and BAN reuests are accepted all other raise an exception."""
        with self.assertRaises(AssertionError):
            self.handler._request("DELETE", self.domain, self.path)
        assert not mock_request.call_count
        self.handler._request("BAN", self.domain, self.path)
        mock_request.assert_called_once_with("BAN", self.url, headers=self.headers)
        mock_request.reset_mock()
        self.handler._request("PURGE", self.domain, self.path)
        mock_request.assert_called_once_with("PURGE", self.url, headers=self.headers)

    @mock.patch("requests.request")
    def test_request_accepts_valid_paths_only(self, mock_request):
        """Accept only a valid path."""
        with self.assertRaises(AssertionError):
            self.handler._request("BAN", self.domain, "^.*$")
        with self.assertRaises(AssertionError):
            self.handler._request("BAN", self.domain, "path/to")
        assert not mock_request.call_count
        self.handler._request("BAN", self.domain, "/path/to")
        self.handler._request("BAN", self.domain, "/path/to/")
        self.handler._request("BAN", self.domain, "/path/to/(.*?)")
        self.handler._request("BAN", self.domain, "/path(.*?).jpg")
        self.handler._request("BAN", self.domain, "/(.*?).jpg")
        self.handler._request("BAN", self.domain, "/")

    @mock.patch("rproxyi.backends.varnish.logger.error")
    @mock.patch("requests.request")
    def test_connection_error_logs_and_finishes(self, mock_request, mock_log):
        """A connection error."""
        mock_request.side_effect = requests.exceptions.ConnectionError
        self.handler._request("BAN", self.domain, self.path)
        msg = f"ConnectionError {self.url}"
        mock_log.assert_called_once_with(msg)

    @mock.patch("rproxyi.backends.varnish.logger.error")
    def test_http_error_logs_and_finishes(self, mock_log):
        """A http error."""
        with HTTMock(response_content):
            self.handler._request("BAN", self.domain, self.path)
        params = (self.url, 500, "FAIL")
        msg = "Problems connecting to {0}: ({1}) {2}".format(*params)  # noqa: SFS201
        mock_log.assert_called_once_with(msg)

    @mock.patch("requests.request")
    def test_ban_results_in_ban_request(self, mock_request):
        """A call of _ban will make a BAN request."""
        self.handler._ban(self.domain, self.path)
        mock_request.assert_called_once_with("BAN", self.url, headers=self.headers)

    @mock.patch("requests.request")
    def test_purge_results_in_purge_request(self, mock_request):
        """A call of _purge will make a PURGE request."""
        self.handler._purge(self.domain, self.path)
        mock_request.assert_called_once_with("PURGE", self.url, headers=self.headers)

    @mock.patch("requests.request")
    def test_invalidate_page_lazy_results_in_ban_request(self, mock_request):
        """When invalidating a page with purge=False a BAN request is made."""
        self.handler.invalidate_page(self.domain, self.path)
        mock_request.assert_called_once_with("BAN", self.url, headers=self.headers)

    @mock.patch("requests.request")
    def test_invalidate_page_immediately_results_in_purge_request(self, mock_request):
        """When invalidating a page with purge=True a PURGE request is made."""
        self.handler.invalidate_page(self.domain, self.path, True)
        mock_request.assert_called_once_with("PURGE", self.url, headers=self.headers)

    @mock.patch("requests.request")
    def test_invalidate_path_results_in_ban_request(self, mock_request):
        """When invalidating a page with purge=False a BAN request is made."""
        self.handler.invalidate_path(self.domain, self.path, False)
        mock_request.assert_called_once_with("BAN", self.url, headers=self.headers)
        mock_request.reset_mock()
        self.handler.invalidate_path(self.domain, self.path, True)
        mock_request.assert_called_once_with("BAN", self.url, headers=self.headers)
