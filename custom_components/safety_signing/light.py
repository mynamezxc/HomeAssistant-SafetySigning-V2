"""Platform for light integration."""
from __future__ import annotations

import logging

import awesomelights
import voluptuous as vol

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    LightEntity
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)



async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add cover for passed config_entry in HA."""
    # The token is loaded from the associated hass.data entry that was created in the
    # __init__.async_setup_entry function
    token = hass.data[DOMAIN][config_entry.entry_id]

    # Add all entities to HA
    async_add_entities(AwesomeLight(cron) for cron in token.crons)


class AwesomeLight(LightEntity):
    """Representation of an Awesome Light."""

    def __init__(self, cron) -> None:
        """Initialize an AwesomeLight."""
        self._cron = cron
        self._light = cron
        self._name = cron.name
        self._state = None
        self._brightness = None

        self._attr_unique_id = f"{self._cron.cron_id}_cron"
        self._attr_name = self._cron.name
        self._attr_token_serial = self._cron.token_serial
        self._attr_serial_number = self._cron.serial_number
        self._attr_pin = self._cron.pin
        self._attr_access_token = self._cron.access_token

    async def async_added_to_hass(self) -> None:
        """Run when this Entity has been added to HA."""
        self._cron.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Entity being removed from hass."""
        self._cron.remove_callback(self.async_write_ha_state)

    @property
    def device_info(self) -> DeviceInfo:
        """Information about this entity/device."""
        return {
            "identifiers": {(DOMAIN, self._cron.cron_id)},
            # If desired, the name for the device could be different to the entity
            "name": self.name,
            "sw_version": self._cron.firmware_version,
            "model": self._cron.model,
            "manufacturer": self._cron.token.manufacturer,
        }

    # This property is important to let HA know if this entity is online or not.
    # If an entity is offline (return False), the UI will refelect this.
    @property
    def available(self) -> bool:
        """Return True if cron and token is available."""
        return self._cron.online and self._cron.token.online

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light.
        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    def turn_on(self, **kwargs) -> None:
        """Instruct the light to turn on.
        You can skip the brightness part if your light does not support
        brightness control.
        """
        self._light.brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        self._light.turn_on()

    def turn_off(self, **kwargs) -> None:
        """Instruct the light to turn off."""
        self._light.turn_off()

    def update(self) -> None:
        """Fetch new state data for this light.
        This is the only method that should fetch new data for Home Assistant.
        """
        self._light.update()
        self._state = self._light.is_on()
        self._brightness = self._light.brightness