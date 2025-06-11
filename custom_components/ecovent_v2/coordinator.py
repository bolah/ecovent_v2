"""VentoUpdateCoordinator class."""

# from __future__ import annotations
from datetime import timedelta
import logging

from ecoventv2 import Fan

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_IP_ADDRESS,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class VentoFanDataUpdateCoordinator(DataUpdateCoordinator):
    """Class for Vento Fan Update Coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        config: ConfigEntry,
    ) -> None:
        """Initialize global Vento data updater."""
        self._config = config
        _LOGGER.error("COORDINATOR.__init__: Creating Fan with config: %s", config.data)
        self._fan = Fan(
            config.data[CONF_IP_ADDRESS],
            config.data[CONF_PASSWORD],
            config.data[CONF_DEVICE_ID],
            config.data[CONF_NAME],
            config.data[CONF_PORT],
        )
        _LOGGER.error("COORDINATOR.__init__: Fan object created: %s", vars(self._fan))
        _LOGGER.error("COORDINATOR.__init__: Calling init_device() [COORDINATOR]")
        self._fan.init_device()
        _LOGGER.error("COORDINATOR.__init__: Fan after init_device: %s", vars(self._fan))
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=60),
            update_method=self._fan.update(),
        )

    async def _async_update_data(self) -> None:
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        self._fan.update()

    def _update_fan(self):
        _LOGGER.error("COORDINATOR._update_fan: About to update fan: %s", vars(self._fan))
        self._fan.update()
        _LOGGER.error("COORDINATOR._update_fan: Fan after update: %s", vars(self._fan))
        return self._fan
