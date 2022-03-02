"""Platform for sensor integration."""
# This file shows the setup for the sensors associated with the cover.
# They are setup in the same way with the call to the async_setup_entry function
# via HA from the module __init__. Each sensor has a device_class, this tells HA how
# to display it in the UI (for know types). The unit_of_measurement property tells HA
# what the unit is, so it can display the correct range. For predefined types (such as
# battery), the unit_of_measurement should match what's expected.
import random

"""Component to interface with switches that can be controlled remotely."""
from __future__ import annotations

from datetime import timedelta
from typing import Any, final

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import Entity
from homeassistant.components.switch import (
    SwitchEntity,
)
from homeassistant.const import (
    STATE_OFF,
    STATE_ON,
    DEVICE_CLASS_RUNNING,
)
from .const import DOMAIN


# This function is called as part of the __init__.async_setup_entry (via the
# hass.config_entries.async_forward_entry_setup call)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    token = hass.data[DOMAIN][config_entry.entry_id]

    new_devices = []
    for cron in token.crons:
        new_devices.append(SwitchCronJob(cron))
        # new_devices.append(IlluminanceSensor(cron))
    if new_devices:
        async_add_entities(new_devices)

class SwitchBase(Entity):
    """Base representation of a Hello World Sensor."""

    should_poll = False

    def __init__(self, cron):
        """Initialize the sensor."""
        self._cron = cron

    # To link this entity to the cover device, this property must return an
    # identifiers value matching that used in the cover, but no other information such
    # as name. If name is returned, this entity will then also become a device in the
    # HA UI.
    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {"identifiers": {(DOMAIN, self._cron.cron_id)}}

    # This property is important to let HA know if this entity is online or not.
    # If an entity is offline (return False), the UI will refelect this.
    @property
    def available(self) -> bool:
        """Return True if cron and token is available."""
        return self._cron.online and self._cron.token.online

    async def async_added_to_hass(self):
        """Run when this Entity has been added to HA."""
        # Sensors should also register callbacks to HA when their state changes
        self._cron.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Entity being removed from hass."""
        # The opposite of async_added_to_hass. Remove any registered call backs here.
        self._cron.remove_callback(self.async_write_ha_state)

class SwitchCronJob(SwitchBase):
    """Base class for switch entities."""
    device_class = DEVICE_CLASS_RUNNING
    _attr_is_on: bool | None = None
    _attr_state: None = None

    def __init__(self, cron):
        """Initialize the sensor."""
        super().__init__(cron)
        self._cron = cron
        self._attr_unique_id = f"{self._cron.cron_id}_cron"
        self._attr_name = f"{self._cron.name} Cron"
        self._is_on = False

    @property
    def is_on(self):
        """If the switch is currently on or off."""
        return self._is_on

    @property
    def name(self):
        """Name of the entity."""
        return self._cron.cron_id

    async def turn_on(self, **kwargs):
        self._cron.running_cron()
        self._is_on = True
        """Turn the entity on."""

    async def turn_off(self, **kwargs):
        self._cron.turn_off_cron()
        self._is_on = False

    async def async_turn_on(self, **kwargs):
        self._cron.running_cron()
        self._is_on = True
        """Turn the entity on."""

    async def async_turn_off(self, **kwargs):
        self._cron.turn_off_cron()
        self._is_on = False
        """Turn the entity off."""

    async def async_toggle(self, **kwargs):
        """Toggle the entity."""

    @property
    def state(self) -> Literal["on", "off"] | None:
        """Return the state of the binary sensor."""
        is_on = self.is_on
        if is_on is None:
            return None
        return STATE_ON if is_on else STATE_OFF