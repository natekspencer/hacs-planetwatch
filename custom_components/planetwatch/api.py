"""API for PlanetWatch bound to Home Assistant OAuth."""
from __future__ import annotations

import logging
import ssl
from typing import cast

import requests
from aiohttp import ClientSession
from homeassistant.helpers.config_entry_oauth2_flow import (
    LocalOAuth2Implementation,
    OAuth2Session,
)
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from requests.packages.urllib3.util import ssl_

from . import pyplanetwatch
from .const import CIPHERS, USER_AGENT

_LOGGER = logging.getLogger(__name__)


class AsyncConfigEntryAuth(pyplanetwatch.AbstractAuth):
    """Provide PlanetWatch authentication tied to an OAuth2 based config entry."""

    def __init__(
        self,
        websession: ClientSession,
        oauth_session: OAuth2Session,
    ) -> None:
        """Initialize NEW_NAME auth."""
        super().__init__(websession)
        self._oauth_session = oauth_session

    async def async_get_access_token(self) -> str:
        """Return a valid access token."""
        if not self._oauth_session.valid_token:
            await self._oauth_session.async_ensure_token_valid()

        return self._oauth_session.token["access_token"]


class TlsAdapter(HTTPAdapter):
    """Tls Adapter."""

    def __init__(self, ssl_options=0, **kwargs):
        self.ssl_options = ssl_options
        super(TlsAdapter, self).__init__(**kwargs)

    def init_poolmanager(self, *pool_args, **pool_kwargs):
        ctx = ssl_.create_urllib3_context(
            ciphers=CIPHERS,
            cert_reqs=ssl.CERT_REQUIRED,
            options=self.ssl_options,
        )
        self.poolmanager = PoolManager(*pool_args, ssl_context=ctx, **pool_kwargs)


class PlanetWatchLocalOAuth2Implementation(LocalOAuth2Implementation):
    """PlanetWatch Local OAuth2 implementation."""

    @property
    def name(self) -> str:
        """Name of the implementation."""
        return "PlanetWatch"

    async def _token_request(self, data: dict) -> dict:
        """Make a token request."""
        data["client_id"] = self.client_id
        headers = {"User-Agent": USER_AGENT}

        def _async_fetch_token():
            session = requests.session()
            adapter = TlsAdapter()
            session.mount("https://", adapter)
            return session.post(self.token_url, data=data, headers=headers)

        resp = await self.hass.async_add_executor_job(_async_fetch_token)

        if resp.status_code >= 400 and _LOGGER.isEnabledFor(logging.DEBUG):
            body = resp.text
            _LOGGER.debug(
                "Token request failed with status=%s, body=%s",
                resp.status_code,
                body,
            )
        resp.raise_for_status()
        return cast(dict, resp.json())
