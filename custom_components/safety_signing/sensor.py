"""Platform for sensor integration."""
# This file shows the setup for the sensors associated with the cover.
# They are setup in the same way with the call to the async_setup_entry function
# via HA from the module __init__. Each sensor has a device_class, this tells HA how
# to display it in the UI (for know types). The unit_of_measurement property tells HA
# what the unit is, so it can display the correct range. For predefined types (such as
# battery), the unit_of_measurement should match what's expected.
import random

from homeassistant.const import (
    ATTR_VOLTAGE,
    # DEVICE_CLASS_BATTERY,
    # DEVICE_CLASS_ILLUMINANCE,
    PERCENTAGE,
)
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.helpers.entity import Entity

from .const import DOMAIN


# See cover.py for more details.
# Note how both entities for each cron sensor (battry and illuminance) are added at
# the same time to the same list. This way only a single async_add_devices call is
# required.

"""Component to interface with binary sensors."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging
from typing import Literal, final

import voluptuous as vol

from homeassistant.backports.enum import StrEnum
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.config_validation import (  # noqa: F401
    PLATFORM_SCHEMA,
    PLATFORM_SCHEMA_BASE,
)
from homeassistant.helpers.entity import Entity, EntityDescription
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "binary_sensor"
SCAN_INTERVAL = timedelta(seconds=30)

ENTITY_ID_FORMAT = DOMAIN + ".{}"


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    token = hass.data[DOMAIN][config_entry.entry_id]

    new_devices = []
    for cron in token.crons:
        new_devices.append(CronSensor(cron))
        # new_devices.append(IlluminanceSensor(cron))
    if new_devices:
        async_add_entities(new_devices)

class BinarySensorDeviceClass(StrEnum):
    """Device class for binary sensors."""
    # On means running, Off means not running
    RUNNING = "running"



DEVICE_CLASS_RUNNING = BinarySensorDeviceClass.RUNNING.value


@dataclass
class BinarySensorEntityDescription(Entity):
    """A class that describes binary sensor entities."""

    device_class: BinarySensorDeviceClass | str | None = None


class CronSensor(Entity):
    """Represent a binary sensor."""

    entity_description: BinarySensorEntityDescription
    

    def __init__(self, cron) -> None:
        super().__init__(cron)
        self._cron = cron
        self._attr_unique_id = f"{self._cron.cron_id}_cron"
        self._attr_name = f"{self._cron.name} Cron"
        self._attr_device_class = DEVICE_CLASS_RUNNING
        self._attr_is_on = False

    @property
    def device_class(self):
        """Return the class of this entity."""
        return self._attr_device_class

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._attr_is_on

    @final
    @property
    def state(self):
        """Return the state of the binary sensor."""
        is_on = self.is_on
        if is_on is None:
            return None
        return STATE_ON if is_on else STATE_OFF