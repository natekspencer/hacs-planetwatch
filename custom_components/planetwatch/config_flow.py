"""Config flow for PlanetWatch."""
import logging

import jwt
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.config_entry_oauth2_flow import AbstractOAuth2FlowHandler

from .api import PlanetWatchLocalOAuth2Implementation
from .const import DOMAIN, OAUTH2_AUTHORIZE, OAUTH2_CLIENTID, OAUTH2_TOKEN


class OAuth2FlowHandler(AbstractOAuth2FlowHandler, domain=DOMAIN):
    """Config flow to handle PlanetWatch OAuth2 authentication."""

    DOMAIN = DOMAIN

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle a flow initialized by the user."""
        await self.async_set_unique_id(DOMAIN)

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        self.async_register_implementation(
            self.hass,
            PlanetWatchLocalOAuth2Implementation(
                self.hass,
                DOMAIN,
                OAUTH2_CLIENTID,
                None,
                OAUTH2_AUTHORIZE,
                OAUTH2_TOKEN,
            ),
        )

        return await super().async_step_user(user_input)

    async def async_oauth_create_entry(self, data: dict) -> FlowResult:
        """Create an entry for the flow."""
        title = jwt.decode(
            data["token"]["access_token"],
            options={"verify_signature": False},
        ).get("preferred_username", self.flow_impl.name)
        return self.async_create_entry(title=title, data=data)

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return logging.getLogger(__name__)
