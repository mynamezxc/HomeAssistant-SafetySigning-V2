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
    DEVICE_CLASS_BATTERY,
    # DEVICE_CLASS_ILLUMINANCE,
    PERCENTAGE,
)
from homeassistant.helpers.entity import Entity

from .const import DOMAIN


# See cover.py for more details.
# Note how both entities for each cron sensor (battry and illuminance) are added at
# the same time to the same list. This way only a single async_add_devices call is
# required.
async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    token = hass.data[DOMAIN][config_entry.entry_id]

    new_devices = []
    for cron in token.crons:
        new_devices.append(SwitchEntity(cron))
        # new_devices.append(IlluminanceSensor(cron))
    if new_devices:
        async_add_entities(new_devices)


# This base class shows the common properties and methods for a sensor as used in this
# example. See each sensor for further details about properties and methods that
# have been overridden.
# class SensorBase(Entity):
#     """Base representation of a Hello World Sensor."""

#     should_poll = False

#     def __init__(self, cron):
#         """Initialize the sensor."""
#         self._cron = cron

#     # To link this entity to the cover device, this property must return an
#     # identifiers value matching that used in the cover, but no other information such
#     # as name. If name is returned, this entity will then also become a device in the
#     # HA UI.
#     @property
#     def device_info(self):
#         """Return information to link this entity with the correct device."""
#         return {"identifiers": {(DOMAIN, self._cron.cron_id)}}

#     # This property is important to let HA know if this entity is online or not.
#     # If an entity is offline (return False), the UI will refelect this.
#     @property
#     def available(self) -> bool:
#         """Return True if cron and token is available."""
#         return self._cron.online and self._cron.token.online

#     async def async_added_to_hass(self):
#         """Run when this Entity has been added to HA."""
#         # Sensors should also register callbacks to HA when their state changes
#         self._cron.register_callback(self.async_write_ha_state)

#     async def async_will_remove_from_hass(self):
#         """Entity being removed from hass."""
#         # The opposite of async_added_to_hass. Remove any registered call backs here.
#         self._cron.remove_callback(self.async_write_ha_state)


# class BatterySensor(SensorBase):
#     """Representation of a Sensor."""

#     # The class of this device. Note the value should come from the homeassistant.const
#     # module. More information on the available devices classes can be seen here:
#     # https://developers.home-assistant.io/docs/core/entity/sensor
#     device_class = DEVICE_CLASS_BATTERY

#     # The unit of measurement for this entity. As it's a DEVICE_CLASS_BATTERY, this
#     # should be PERCENTAGE. A number of units are supported by HA, for some
#     # examples, see:
#     # https://developers.home-assistant.io/docs/core/entity/sensor#available-device-classes
#     _attr_unit_of_measurement = PERCENTAGE

#     def __init__(self, cron):
#         """Initialize the sensor."""
#         super().__init__(cron)

#         # As per the sensor, this must be a unique value within this domain. This is done
#         # by using the device ID, and appending "_battery"
#         self._attr_unique_id = f"{self._cron.cron_id}_battery"

#         # The name of the entity
#         self._attr_name = f"{self._cron.name} Battery"

#         self._state = random.randint(0, 100)

#     # The value of this sensor. As this is a DEVICE_CLASS_BATTERY, this value must be
#     # the battery level as a percentage (between 0 and 100)
#     @property
#     def state(self):
#         """Return the state of the sensor."""
#         return self._cron.battery_level


# # This is another sensor, but more simple compared to the battery above. See the
# # comments above for how each field works.











"""Component to interface with switches that can be controlled remotely."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging
from typing import Any, final

import voluptuous as vol

from homeassistant.backports.enum import StrEnum
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    SERVICE_TOGGLE,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_ON,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.config_validation import (  # noqa: F401
    PLATFORM_SCHEMA,
    PLATFORM_SCHEMA_BASE,
)
from homeassistant.helpers.entity import ToggleEntity, ToggleEntityDescription
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.typing import ConfigType
from homeassistant.loader import bind_hass

DOMAIN = "switch"
SCAN_INTERVAL = timedelta(seconds=30)

ENTITY_ID_FORMAT = DOMAIN + ".{}"

ATTR_TODAY_ENERGY_KWH = "today_energy_kwh"
ATTR_CURRENT_POWER_W = "current_power_w"

MIN_TIME_BETWEEN_SCANS = timedelta(seconds=10)

PROP_TO_ATTR = {
    "current_power_w": ATTR_CURRENT_POWER_W,
    "today_energy_kwh": ATTR_TODAY_ENERGY_KWH,
}

_LOGGER = logging.getLogger(__name__)


class SwitchDeviceClass(StrEnum):
    """Device class for switches."""

    OUTLET = "outlet"
    SWITCH = "switch"


DEVICE_CLASSES_SCHEMA = vol.All(vol.Lower, vol.Coerce(SwitchDeviceClass))

# DEVICE_CLASS* below are deprecated as of 2021.12
# use the SwitchDeviceClass enum instead.
DEVICE_CLASSES = [cls.value for cls in SwitchDeviceClass]
DEVICE_CLASS_OUTLET = SwitchDeviceClass.OUTLET.value
DEVICE_CLASS_SWITCH = SwitchDeviceClass.SWITCH.value


@bind_hass
def is_on(hass: HomeAssistant, entity_id: str) -> bool:
    """Return if the switch is on based on the statemachine.
    Async friendly.
    """
    return hass.states.is_state(entity_id, STATE_ON)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Track states and offer events for switches."""
    component = hass.data[DOMAIN] = EntityComponent(
        _LOGGER, DOMAIN, hass, SCAN_INTERVAL
    )
    await component.async_setup(config)

    component.async_register_entity_service(SERVICE_TURN_OFF, {}, "async_turn_off")
    component.async_register_entity_service(SERVICE_TURN_ON, {}, "async_turn_on")
    component.async_register_entity_service(SERVICE_TOGGLE, {}, "async_toggle")

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
class SwitchEntityDescription(ToggleEntityDescription):
    """A class that describes switch entities."""

    device_class: SwitchDeviceClass | str | None = None


class SwitchEntity(ToggleEntity):
    """Base class for switch entities."""

    entity_description: SwitchEntityDescription
    _attr_current_power_w: float | None = None
    _attr_device_class: SwitchDeviceClass | str | None
    _attr_today_energy_kwh: float | None = None

    def __init__(self, cron):
        """Initialize the sensor."""
        super().__init__(cron)

        # As per the sensor, this must be a unique value within this domain. This is done
        # by using the device ID, and appending "_battery"
        self._attr_unique_id = f"{self._cron.cron_id}_cron"
        # The name of the entity
        self._attr_name = f"{self._cron.name} Cron"
        self._state = random.randint(0, 100)

    @property
    def current_power_w(self) -> float | None:
        """Return the current power usage in W."""
        return self._attr_current_power_w

    @property
    def device_class(self) -> SwitchDeviceClass | str | None:
        """Return the class of this entity."""
        if hasattr(self, "_attr_device_class"):
            return self._attr_device_class
        if hasattr(self, "entity_description"):
            return self.entity_description.device_class
        return None

    @property
    def today_energy_kwh(self) -> float | None:
        """Return the today total energy usage in kWh."""
        return self._attr_today_energy_kwh

    @final
    @property
    def state_attributes(self) -> dict[str, Any] | None:
        """Return the optional state attributes."""
        data = {}

        for prop, attr in PROP_TO_ATTR.items():
            value = getattr(self, prop)
            if value is not None:
                data[attr] = value
        return data