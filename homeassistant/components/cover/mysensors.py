"""
Support for MySensors covers.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/cover.mysensors/
"""
from homeassistant.components import mysensors
from homeassistant.components.cover import ATTR_POSITION, DOMAIN, CoverDevice
from homeassistant.const import STATE_OFF, STATE_ON


async def async_setup_platform(
        hass, config, async_add_devices, discovery_info=None):
    """Set up the mysensors platform for covers."""
    mysensors.setup_mysensors_platform(
        hass, DOMAIN, discovery_info, MySensorsCover,
        async_add_devices=async_add_devices)


class MySensorsCover(mysensors.MySensorsEntity, CoverDevice):
    """Representation of the value of a MySensors Cover child node."""

    @property
    def assumed_state(self):
        """Return True if unable to access real state of entity."""
        return self.gateway.optimistic

    @property
    def is_closed(self):
        """Return True if cover is closed."""
        set_req = self.gateway.const.SetReq
        if set_req.V_DIMMER in self._values:
            return self._values.get(set_req.V_DIMMER) == 0
        return self._values.get(set_req.V_LIGHT) == STATE_OFF

    @property
    def current_cover_position(self):
        """Return current position of cover.

        None is unknown, 0 is closed, 100 is fully open.
        """
        set_req = self.gateway.const.SetReq
        return self._values.get(set_req.V_DIMMER)

    def open_cover(self, **kwargs):
        """Move the cover up."""
        set_req = self.gateway.const.SetReq
        self.gateway.set_child_value(
            self.node_id, self.child_id, set_req.V_UP, 1)
        if self.gateway.optimistic:
            # Optimistically assume that cover has changed state.
            if set_req.V_DIMMER in self._values:
                self._values[set_req.V_DIMMER] = 100
            else:
                self._values[set_req.V_LIGHT] = STATE_ON
            self.schedule_update_ha_state()

    def close_cover(self, **kwargs):
        """Move the cover down."""
        set_req = self.gateway.const.SetReq
        self.gateway.set_child_value(
            self.node_id, self.child_id, set_req.V_DOWN, 1)
        if self.gateway.optimistic:
            # Optimistically assume that cover has changed state.
            if set_req.V_DIMMER in self._values:
                self._values[set_req.V_DIMMER] = 0
            else:
                self._values[set_req.V_LIGHT] = STATE_OFF
            self.schedule_update_ha_state()

    def set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        position = kwargs.get(ATTR_POSITION)
        set_req = self.gateway.const.SetReq
        self.gateway.set_child_value(
            self.node_id, self.child_id, set_req.V_DIMMER, position)
        if self.gateway.optimistic:
            # Optimistically assume that cover has changed state.
            self._values[set_req.V_DIMMER] = position
            self.schedule_update_ha_state()

    def stop_cover(self, **kwargs):
        """Stop the device."""
        set_req = self.gateway.const.SetReq
        self.gateway.set_child_value(
            self.node_id, self.child_id, set_req.V_STOP, 1)
