import logging
from blinker import Signal

STATE_UNLOCKED = "UNLOCKED"
STATE_LOCKED = "LOCKED"
STATE_UNDEFINED = "UNDEFINED"


class DoorState(object):

    def __init__(self, identifier, initial_state=STATE_UNDEFINED):
        self._logger = logging.getLogger("{} ({})".format(__name__, identifier))
        self._state = initial_state
        self.on_change = Signal()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if self._state == value:
            return
        self._logger.info("state changed: {} -> {}".format(self._state, value))
        self._state = value
        self.on_change.send(self)
