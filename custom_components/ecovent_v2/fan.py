"""Support for Blauberg Vento Expert Fans with api v.2."""

from __future__ import annotations

from typing import Any
import asyncio
import logging

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.device_registry import DeviceInfo
from .const import SERVICE_FILTER_TIMER_RESET
from .const import SERVICE_RESET_ALARMS
from .const import DOMAIN
from .coordinator import VentoFanDataUpdateCoordinator

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

_LOGGER = logging.getLogger(__name__)

DEFAULT_ON_PERCENTAGE = 5
SPEED_RANGE = (1, 3)  # off is not included

FULL_SUPPORT = (
    FanEntityFeature.SET_SPEED
    | FanEntityFeature.PRESET_MODE
    | FanEntityFeature.OSCILLATE
    | FanEntityFeature.DIRECTION
    | FanEntityFeature.TURN_OFF
    | FanEntityFeature.TURN_ON
)


PRESET_MODES = ["low", "medium", "high", "manual"]
DIRECTIONS = ["ventilation", "air_supply", "heat_recovery"]


async def async_setup_entry(
    hass: HomeAssistant,
    config: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Ecovent Fan config entry."""
    async_add_entities([VentoExpertFan(hass, config)])

    platform = entity_platform.async_get_current_platform()

    # This will call VentoExpertFan.async_reset_filter_timer()
    platform.async_register_entity_service(
        SERVICE_FILTER_TIMER_RESET, {}, VentoExpertFan.async_reset_filter_timer
    )
    # This will call VentoExpertFana.sync_reset_alarms()
    platform.async_register_entity_service(
        SERVICE_RESET_ALARMS, {}, VentoExpertFan.async_reset_alarms
    )


class VentoExpertFan(CoordinatorEntity, FanEntity):
    """Cento Expert Coordinator Class."""

    def __init__(self, hass: HomeAssistant, config: ConfigEntry) -> None:
        """Initialize fan."""

        coordinator: VentoFanDataUpdateCoordinator = hass.data[DOMAIN][config.entry_id]
        super().__init__(coordinator)

        self._fan = coordinator._fan
        self._percentage = self._fan.man_speed
        self._attr_unique_id = self._fan.id
        self._attr_name = self._fan.name
        self._attr_extra_state_attributes = {"ipv4_address": self._fan.curent_wifi_ip}
        self._attr_supported_features = FULL_SUPPORT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._fan.id)},
            name=self._fan.name,
            model=self._fan.unit_type,
            sw_version=self._fan.firmware,
            manufacturer="Blauberg",
            configuration_url=f"http://{self._fan.curent_wifi_ip}",
        )

    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        return self._attr_extra_state_attributes

    @property
    def name(self) -> str:
        """Get entity name."""
        return self._fan.name

    @property
    def unique_id(self) -> str:
        """Return the unique id."""
        return self._fan.id

    @property
    def is_on(self) -> bool:
        """Return state."""
        return self._fan.state == "on"

    @property
    def percentage(self) -> int:
        """Return the current speed."""
        return self._percentage

    @property
    def preset_modes(self) -> list[str]:
        """Return a list of available preset modes."""
        return PRESET_MODES

    @property
    def directions(self) -> list[str]:
        """Return a list of available preset modes."""
        return DIRECTIONS

    @property
    def preset_mode(self) -> str:
        """Return the current preset mode, e.g., auto, smart, interval, favorite."""
        return self._fan.speed

    @property
    def current_direction(self) -> str:
        """Fan direction."""
        return self._fan.airflow

    @property
    def oscillating(self) -> bool:
        """Oscillating."""
        return self._fan.airflow == "heat_recovery"

    @property
    def boost_time(self) -> int:
        """Boost time."""
        return self._fan.boost_time

    @property
    def humidity_treshold(self) -> int:
        """Boost time."""
        return self._fan.humidity_treshold

    @property
    def analogV_treshold(self) -> int:
        """Boost time."""
        return self._fan.analogV_treshold

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the entity."""
        _LOGGER.error("ASYNC_TURN_ON CALLED with percentage: %s, preset_mode: %s", percentage, preset_mode)
        try:
            _LOGGER.error("ASYNC_TURN_ON: Starting turn on process")
            if preset_mode is not None:
                _LOGGER.error("ASYNC_TURN_ON: Setting preset mode: %s", preset_mode)
                self.set_preset_mode(preset_mode)
            if percentage is not None:
                _LOGGER.error("ASYNC_TURN_ON: Setting percentage: %s", percentage)
                self.set_percentage(percentage)
            _LOGGER.error("ASYNC_TURN_ON: Setting fan state to 'on'")
            self._fan.set_param("state", "on")
            _LOGGER.error("ASYNC_TURN_ON: Requesting coordinator refresh")
            await self.coordinator.async_request_refresh()
            _LOGGER.error("ASYNC_TURN_ON: Completed successfully")
        except Exception as err:
            _LOGGER.error("ASYNC_TURN_ON: Error turning on fan: %s", err)
            raise

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the entity."""
        _LOGGER.error("ASYNC_TURN_OFF CALLED")
        try:
            _LOGGER.error("ASYNC_TURN_OFF: Starting turn off process")
            _LOGGER.error("ASYNC_TURN_OFF: Setting fan state to 'off'")
            self._fan.set_param("state", "off")
            _LOGGER.error("ASYNC_TURN_OFF: Requesting coordinator refresh")
            await self.coordinator.async_request_refresh()
            _LOGGER.error("ASYNC_TURN_OFF: Completed successfully")
        except Exception as err:
            _LOGGER.error("ASYNC_TURN_OFF: Error turning off fan: %s", err)
            raise

    def set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        _LOGGER.error("SET_PRESET_MODE CALLED with: %s", preset_mode)
        if preset_mode in self.preset_modes:
            _LOGGER.error("SET_PRESET_MODE: Setting fan speed to: %s", preset_mode)
            self._fan.set_param("speed", preset_mode)
            if preset_mode == "manual":
                _LOGGER.error("SET_PRESET_MODE: Setting manual speed percent to: %s", self.percentage)
                self._fan.set_man_speed_percent(self.percentage)
        else:
            _LOGGER.error("SET_PRESET_MODE: Invalid preset mode: %s", preset_mode)
            raise ValueError(f"Invalid preset mode: {preset_mode}")

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        _LOGGER.error("ASYNC_SET_PRESET_MODE CALLED with: %s", preset_mode)
        self.set_preset_mode(preset_mode)
        await self.coordinator.async_refresh()

    def set_percentage(self, percentage: int) -> None:
        """Set the speed of the fan, as a percentage."""
        _LOGGER.error("SET_PERCENTAGE CALLED with: %s", percentage)
        self._percentage = percentage
        if self._fan.speed == "manual":
            _LOGGER.error("SET_PERCENTAGE: Setting manual speed percent to: %s", percentage)
            self._fan.set_man_speed_percent(percentage)

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed of the fan, as a percentage."""
        _LOGGER.error("ASYNC_SET_PERCENTAGE CALLED with: %s", percentage)
        self.set_percentage(percentage)
        await self.coordinator.async_refresh()

    async def async_set_direction(self, direction: str) -> None:
        """Set the direction of the fan."""
        if direction == "forward" and self._fan.airflow != "ventilation":
            self._fan.set_param("airflow", "ventilation")
        if direction == "reverse" and self._fan.airflow != "air_supply":
            self._fan.set_param("airflow", "air_supply")
        await self.coordinator.async_refresh()
        # self.schedule_update_ha_state()

    async def async_oscillate(self, oscillating: bool) -> None:
        """Set oscillation."""
        if oscillating:
            self._fan.set_param("airflow", "heat_recovery")
        else:
            self._fan.set_param("airflow", "ventilation")
        await self.coordinator.async_refresh()
        # self.schedule_update_ha_state()

        # Custom services

    # Reset filter timer
    async def async_reset_filter_timer(self, fan_target) -> None:
        """Reset Fan's filter timer."""
        self._fan.set_param("filter_timer_reset", "")

    # Reset alarms
    async def async_reset_alarms(self, fan_target) -> None:
        """Reset Fan's Alarms."""
        self._fan.set_param("reset_alarms", "")
