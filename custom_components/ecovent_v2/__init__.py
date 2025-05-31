"""The EcoVent_v2 integration."""
# from __future__ import annotations
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import VentoFanDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# PLATFORMS: list[str] = ["sensor", "binary_sensor", "switch", "fan"]

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.FAN,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up EcoVent_v2 from a config entry."""
    _LOGGER.error("ASYNC_SETUP_ENTRY: Starting setup for entry: %s", entry.entry_id)
    
    try:
        _LOGGER.error("ASYNC_SETUP_ENTRY: Creating coordinator")
        coordinator = VentoFanDataUpdateCoordinator(
            hass,
            entry,
        )
        _LOGGER.error("ASYNC_SETUP_ENTRY: Coordinator created successfully")

        _LOGGER.error("ASYNC_SETUP_ENTRY: Starting first refresh")
        await coordinator.async_config_entry_first_refresh()
        _LOGGER.error("ASYNC_SETUP_ENTRY: First refresh completed")

        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = coordinator
        _LOGGER.error("ASYNC_SETUP_ENTRY: Coordinator stored in hass.data")

        _LOGGER.error("ASYNC_SETUP_ENTRY: Setting up platforms: %s", PLATFORMS)
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        _LOGGER.error("ASYNC_SETUP_ENTRY: All platforms setup completed")

        return True
    except Exception as err:
        _LOGGER.error("ASYNC_SETUP_ENTRY: Error during setup: %s", err)
        raise


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    return unload_ok
