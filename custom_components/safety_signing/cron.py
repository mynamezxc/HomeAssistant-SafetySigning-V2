"""Support for Coinbase sensors."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

ATTR_NATIVE_BALANCE = "Balance in native currency"

CURRENCY_ICONS = {
    "BTC": "mdi:currency-btc",
    "ETH": "mdi:currency-eth",
    "EUR": "mdi:currency-eur",
    "LTC": "mdi:litecoin",
    "USD": "mdi:currency-usd",
}

DEFAULT_COIN_ICON = "mdi:cash"

ATTRIBUTION = "Data provided by coinbase.com"

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
    async_add_entities(CronJobSensor(cron) for cron in token.crons)


class CronJobSensor(SensorEntity):
    """Representation of a Coinbase.com sensor."""

    def __init__(self, cron):
        """Initialize the sensor."""
        self._cron = cron
        self._attr_unique_id = f"{self._cron.cron_id}_cover"
        self._attr_name = self._cron.name
        self._attr_token_serial = self._cron.token_serial
        self._attr_serial_number = self._cron.serial_number
        self._attr_pin = self._cron.pin
        self._attr_access_token = self._cron.access_token
        self._attr_state_class = SensorStateClass.TOTAL
        self._attr_device_info = DeviceInfo(
            configuration_url="https://www.coinbase.com/settings/api",
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, self._coinbase_data.user_id)},
            manufacturer="Coinbase.com",
            name=f"Coinbase {self._coinbase_data.user_id[-4:]}",
        )

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return the Unique ID of the sensor."""
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
        return CURRENCY_ICONS.get(self._unit_of_measurement, DEFAULT_COIN_ICON)

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        return {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            ATTR_NATIVE_BALANCE: f"{self._native_balance} {self._native_currency}",
        }

    def update(self):
        """Get the latest state of the sensor."""
        
