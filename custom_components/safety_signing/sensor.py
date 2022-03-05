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

    # On means low, Off means normal
    BATTERY = "battery"

    # On means charging, Off means not charging
    BATTERY_CHARGING = "battery_charging"

    # On means carbon monoxide detected, Off means no carbon monoxide (clear)
    CO = "carbon_monoxide"

    # On means cold, Off means normal
    COLD = "cold"

    # On means connected, Off means disconnected
    CONNECTIVITY = "connectivity"

    # On means open, Off means closed
    DOOR = "door"

    # On means open, Off means closed
    GARAGE_DOOR = "garage_door"

    # On means gas detected, Off means no gas (clear)
    GAS = "gas"

    # On means hot, Off means normal
    HEAT = "heat"

    # On means light detected, Off means no light
    LIGHT = "light"

    # On means open (unlocked), Off means closed (locked)
    LOCK = "lock"

    # On means wet, Off means dry
    MOISTURE = "moisture"

    # On means motion detected, Off means no motion (clear)
    MOTION = "motion"

    # On means moving, Off means not moving (stopped)
    MOVING = "moving"

    # On means occupied, Off means not occupied (clear)
    OCCUPANCY = "occupancy"

    # On means open, Off means closed
    OPENING = "opening"

    # On means plugged in, Off means unplugged
    PLUG = "plug"

    # On means power detected, Off means no power
    POWER = "power"

    # On means home, Off means away
    PRESENCE = "presence"

    # On means problem detected, Off means no problem (OK)
    PROBLEM = "problem"

    # On means running, Off means not running
    RUNNING = "running"

    # On means unsafe, Off means safe
    SAFETY = "safety"

    # On means smoke detected, Off means no smoke (clear)
    SMOKE = "smoke"

    # On means sound detected, Off means no sound (clear)
    SOUND = "sound"

    # On means tampering detected, Off means no tampering (clear)
    TAMPER = "tamper"

    # On means update available, Off means up-to-date
    UPDATE = "update"

    # On means vibration detected, Off means no vibration
    VIBRATION = "vibration"

    # On means open, Off means closed
    WINDOW = "window"


DEVICE_CLASSES_SCHEMA = vol.All(vol.Lower, vol.Coerce(BinarySensorDeviceClass))

# DEVICE_CLASS* below are deprecated as of 2021.12
# use the BinarySensorDeviceClass enum instead.
DEVICE_CLASSES = [cls.value for cls in BinarySensorDeviceClass]
DEVICE_CLASS_BATTERY = BinarySensorDeviceClass.BATTERY.value
DEVICE_CLASS_BATTERY_CHARGING = BinarySensorDeviceClass.BATTERY_CHARGING.value
DEVICE_CLASS_CO = BinarySensorDeviceClass.CO.value
DEVICE_CLASS_COLD = BinarySensorDeviceClass.COLD.value
DEVICE_CLASS_CONNECTIVITY = BinarySensorDeviceClass.CONNECTIVITY.value
DEVICE_CLASS_DOOR = BinarySensorDeviceClass.DOOR.value
DEVICE_CLASS_GARAGE_DOOR = BinarySensorDeviceClass.GARAGE_DOOR.value
DEVICE_CLASS_GAS = BinarySensorDeviceClass.GAS.value
DEVICE_CLASS_HEAT = BinarySensorDeviceClass.HEAT.value
DEVICE_CLASS_LIGHT = BinarySensorDeviceClass.LIGHT.value
DEVICE_CLASS_LOCK = BinarySensorDeviceClass.LOCK.value
DEVICE_CLASS_MOISTURE = BinarySensorDeviceClass.MOISTURE.value
DEVICE_CLASS_MOTION = BinarySensorDeviceClass.MOTION.value
DEVICE_CLASS_MOVING = BinarySensorDeviceClass.MOVING.value
DEVICE_CLASS_OCCUPANCY = BinarySensorDeviceClass.OCCUPANCY.value
DEVICE_CLASS_OPENING = BinarySensorDeviceClass.OPENING.value
DEVICE_CLASS_PLUG = BinarySensorDeviceClass.PLUG.value
DEVICE_CLASS_POWER = BinarySensorDeviceClass.POWER.value
DEVICE_CLASS_PRESENCE = BinarySensorDeviceClass.PRESENCE.value
DEVICE_CLASS_PROBLEM = BinarySensorDeviceClass.PROBLEM.value
DEVICE_CLASS_RUNNING = BinarySensorDeviceClass.RUNNING.value
DEVICE_CLASS_SAFETY = BinarySensorDeviceClass.SAFETY.value
DEVICE_CLASS_SMOKE = BinarySensorDeviceClass.SMOKE.value
DEVICE_CLASS_SOUND = BinarySensorDeviceClass.SOUND.value
DEVICE_CLASS_TAMPER = BinarySensorDeviceClass.TAMPER.value
DEVICE_CLASS_UPDATE = BinarySensorDeviceClass.UPDATE.value
DEVICE_CLASS_VIBRATION = BinarySensorDeviceClass.VIBRATION.value
DEVICE_CLASS_WINDOW = BinarySensorDeviceClass.WINDOW.value


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Track states and offer events for binary sensors."""
    component = hass.data[DOMAIN] = EntityComponent(
        logging.getLogger(__name__), DOMAIN, hass, SCAN_INTERVAL
    )

    await component.async_setup(config)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a config entry."""
    component: EntityComponent = hass.data[DOMAIN]
    return await component.async_setup_entry(entry)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    component: EntityComponent = hass.data[DOMAIN]
    return await component.async_unload_entry(entry)


@dataclass
class BinarySensorEntityDescription(EntityDescription):
    """A class that describes binary sensor entities."""

    device_class: BinarySensorDeviceClass | str | None = None


class CronSensor(Entity):
    """Represent a binary sensor."""

    entity_description: BinarySensorEntityDescription
    _attr_device_class: DEVICE_CLASS_RUNNING
    _attr_is_on: bool | None = None
    _attr_state: None = None

    @property
    def device_class(self) -> BinarySensorDeviceClass | str | None:
        """Return the class of this entity."""
        if hasattr(self, "_attr_device_class"):
            return self._attr_device_class
        if hasattr(self, "entity_description"):
            return self.entity_description.device_class
        return None

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self._attr_is_on

    @final
    @property
    def state(self) -> Literal["on", "off"] | None:
        """Return the state of the binary sensor."""
        is_on = self.is_on
        if is_on is None:
            return None
        return STATE_ON if is_on else STATE_OFF