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
        self._fan = Fan(
            config.data[CONF_IP_ADDRESS],
            config.data[CONF_PASSWORD],
            config.data[CONF_DEVICE_ID],
            config.data[CONF_NAME],
            config.data[CONF_PORT],
        )
        self._fan.init_device()

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=5),  # More frequent updates
            update_method=self._update_fan,
        )

    def _update_fan(self):
        """Update fan data and return the fan object."""
        try:
            _LOGGER.error("_UPDATE_FAN: Starting fan update")
            result = self._fan.update()
            _LOGGER.error("_UPDATE_FAN: Fan update completed, result: %s", result)
            _LOGGER.error("_UPDATE_FAN: Fan state: %s", self._fan.state)
            _LOGGER.error("_UPDATE_FAN: Fan speed: %s", self._fan.speed)
            _LOGGER.error("_UPDATE_FAN: Returning fan object")
            return self._fan
        except Exception as err:
            _LOGGER.error("_UPDATE_FAN: Error updating fan data: %s", err)
            raise UpdateFailed(f"Error communicating with fan: {err}")

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        _LOGGER.error("_ASYNC_UPDATE_DATA: Called")
        try:
            result = await self.hass.async_add_executor_job(self._update_fan)
            _LOGGER.error("_ASYNC_UPDATE_DATA: Executor job completed, result: %s", result)
            return result
        except Exception as err:
            _LOGGER.error("_ASYNC_UPDATE_DATA: Error in async update: %s", err)
            raise

    async def async_request_refresh(self):
        """Request a refresh."""
        _LOGGER.error("ASYNC_REQUEST_REFRESH: Called")
        try:
            await super().async_request_refresh()
            _LOGGER.error("ASYNC_REQUEST_REFRESH: Completed successfully")
        except Exception as err:
            _LOGGER.error("ASYNC_REQUEST_REFRESH: Error: %s", err)
            raise
