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
from homeassistant.components.switch import (
    SwitchEntity,
)
from .const import DOMAIN


# This function is called as part of the __init__.async_setup_entry (via the
# hass.config_entries.async_forward_entry_setup call)
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
    async_add_entities(SwitchCronJob(cron) for cron in token.crons)

class SwitchCronJob(SwitchEntity):
    """Base class for switch entities."""

    def __init__(self, cron):
        """Initialize the sensor."""
        super().__init__(cron)
        self._cron = cron
        # As per the sensor, this must be a unique value within this domain. This is done
        # by using the device ID, and appending "_battery"
        self._attr_unique_id = f"{self._cron.cron_id}_cron"
        # The name of the entity
        self._attr_name = f"{self._cron.name} Cron"

    async def async_turn_on(self, **kwargs):
        self._cron.running_cron()
        """Turn the entity on."""

    async def async_turn_off(self, **kwargs):
        self._cron.turn_off_cron()
        """Turn the entity off."""

    async def async_toggle(self, **kwargs):
        """Toggle the entity."""
