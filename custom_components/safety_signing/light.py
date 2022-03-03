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

from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.entity import DeviceInfo
ATTRIBUTION = "Api provided by TS24 Corp"

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
    async_add_entities(WebServiceSensor(cron) for cron in token.crons)


class WebServiceSensor(SensorEntity):
    """Representation of a Coinbase.com sensor."""

    def __init__(self, cron):
        """Initialize the sensor."""
        self._cron = cron
        self._attr_unique_id = f"{self._cron.cron_id}_cron"
        self._attr_name = f"{self._cron.name} Cron"
        self._is_on = False
        self._state = 0
        self._unit_of_measurement = "time"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_info = DeviceInfo(
            configuration_url="http://localhost:3000/api/",
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, self._cron.cron_id)},
            manufacturer="TS24 Corp",
            name=f"{self._cron.name}",
        )

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._id

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement this sensor expresses itself in."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return "mdi:axis-z-arrow"

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        return {ATTR_ATTRIBUTION: ATTRIBUTION}

    def update(self):
        """Get the latest state of the sensor."""
        self._coinbase_data.update()
        self._state = round(
            1 / float(self._coinbase_data.exchange_rates.rates[self.currency]), 2
        )