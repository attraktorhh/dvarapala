
import logging

from config import (MESSAGE_OPEN_FOR_PUBLIC, MESSAGE_OPEN_FOR_MEMBERS,
                    MESSAGE_CLOSED, MESSAGE_UNDEFINED)

from blinker import Signal

ESTATE_OPEN_FOR_MEMBERS = "open_for_members"
ESTATE_OPEN_FOR_PUBLIC = "open_for_public"
ESTATE_CLOSED = "closed"
ESTATE_UNDEFINED = "unknown"

ALL_ESTATES = [ESTATE_OPEN_FOR_MEMBERS,
               ESTATE_OPEN_FOR_PUBLIC,
               ESTATE_CLOSED,
               ESTATE_UNDEFINED]


def message_by_state(state):
    if state == ESTATE_OPEN_FOR_PUBLIC:
        return MESSAGE_OPEN_FOR_PUBLIC
    elif state == ESTATE_OPEN_FOR_MEMBERS:
        return MESSAGE_OPEN_FOR_MEMBERS
    elif state == ESTATE_CLOSED:
        return MESSAGE_CLOSED
    else:
        return MESSAGE_UNDEFINED

class StateChooserButton(object):
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._ext_state = ESTATE_UNDEFINED
        self.on_change = Signal()

    @property
    def ext_state(self):
        return self._ext_state

    @ext_state.setter
    def ext_state(self, value):
        if value == self._ext_state:
            return
        prev_state = self._ext_state
        if value in ALL_ESTATES:
            self._ext_state = value
        else:
            self._ext_state = ESTATE_UNDEFINED
        self._logger.info(
            "state changed: {} -> {}".format(prev_state, self._ext_state))
        self.on_change.send(self)
