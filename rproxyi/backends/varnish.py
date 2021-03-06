# -*- coding: utf-8 -*-
"""Varnish cache invalidation."""
# Standard Library
import logging
import warnings
from urllib.parse import urlparse

# 3rd-party
import requests

# Local
from .base import CacheInvalidationHandler

logger = logging.getLogger(__name__)


class VarnishCache(CacheInvalidationHandler):
    """Cache invalidation handler for varnish."""

    def _request(self, method, domain, path):
        """Abstract the request to the proxy."""
        assert method in ["BAN", "PURGE"]  # nosec
        headers = {"host": domain}
        url = self.location + path
        parsed = urlparse(url)
        assert parsed.netloc == urlparse(self.location).netloc  # nosec
        assert path.startswith(parsed.path)  # nosec
        logger.debug(f"Method: {method} Url: {url} Path: {path}")
        try:
            response = requests.request(method, url, headers=headers)
        except requests.exceptions.ConnectionError:
            logger.error(f"ConnectionError {url}")
            return
        if response.status_code != 200:
            msg = "Problems connecting to {0}: ({1}) {2}".format(  # noqa: SFS201
                url,
                getattr(response, "status_code", "n/a"),
                getattr(response, "text", "n/a"),
            )
            logger.error(msg)

    def _ban(self, domain, path):
        """
        Issue a ban request.

        This assumes you have something like this in the vcl_recv your vcl:

        if (req.method == "BAN") {
            if (!client.ip ~ purgers) {
                return (synth(405, "Not allowed to BAN"));
            }
            ban("req.http.host == " + req.http.host +
                " && req.url ~ " + req.url);
            # Throw a synthetic page so the request won't go to the backend.
            return(synth(200, "Ban added for "+ req.http.host + " @ " + req.url));
        }
        """
        self._request("BAN", domain, path)

    def _purge(self, domain, path):
        """
        Issue a purge request.

        This assumes you have something like this in the vcl_recv your vcl:

        if (req.method == "PURGE") {
            if (!client.ip ~ purgers) {
                return (synth(405, "Not allowed to PURGE"));
            }
            return (purge);
        }
        """
        self._request("PURGE", domain, path)

    def invalidate_page(self, domain, path, purge=False):
        """
        Invalidate a single page.

        If purge is true then the page gets evicted from the cache immediately.
        """
        if purge:
            self._purge(domain, path)
        else:
            self._ban(domain, path)

    def invalidate_path(self, domain, path, purge=False):
        """
        Invalidate an entire path.

        The path can contain a regular expression to be invalidated.
        If purge is true then the page gets evicted from the cache immediately.
        """
        if purge:
            warnings.warn("Purge not implemented for invalidate_path")
        self._ban(domain, path)
