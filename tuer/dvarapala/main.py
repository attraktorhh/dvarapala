#!/usr/bin/env python
# coding=utf-8

import logging
from threading import Timer

import arrow

import door_state
from serial_communicator import (
    SerialCommunicator, LED_OPEN_PUBLIC, LED_OPEN_MEMBERS, LED_CLOSED)
import state_chooser_button
import twitter
import mqtt_homie

from config import PUBLIC_DEBOUNCE_SECS


class Dvarapala(object):

    def __init__(self):
        self._logger = logging.getLogger(__name__)

        self.d_main = door_state.DoorState("main")
        self.d_kitchen = door_state.DoorState("kitchen")
        self.d_lounge = door_state.DoorState("lounge")
        self.d_back = door_state.DoorState("back")

        self.button = state_chooser_button.StateChooserButton()

        self.serial_communicator = SerialCommunicator(
            self.d_main, self.d_kitchen, self.d_lounge, self.d_back,
            self.button)

        self.state_open = None
        self.state_last_change = arrow.get(0)
        self.state_ext_open_detail = state_chooser_button.ESTATE_UNDEFINED

        self.public_state_open = self.state_open
        self.public_state_last_change = self.state_last_change
        self.public_state_ext_open_detail = self.state_ext_open_detail

        self.timer = None

        self.publishers = [twitter, mqtt_homie]

        self._set_public_state()

    def on_main_door_changed(self, sender):
        """
        @type sender: door_state.DoorState
        """
        self._logger.debug("main door changed")
        if sender.state == door_state.STATE_UNLOCKED:
            self._set_state(state_chooser_button.ESTATE_OPEN_FOR_MEMBERS)
        elif sender.state == door_state.STATE_LOCKED:
            self._set_state(state_chooser_button.ESTATE_CLOSED)

    def _set_state(self, detail_state):
        # set current state
        self.state_last_change = arrow.utcnow()
        self.state_ext_open_detail = detail_state
        self.state_open = self.state_ext_open_detail in [
            state_chooser_button.ESTATE_OPEN_FOR_PUBLIC,
            state_chooser_button.ESTATE_OPEN_FOR_MEMBERS]
        if detail_state is None or detail_state == state_chooser_button.ESTATE_UNDEFINED:
            self.state_open = None
        self._logger.info("state changed to {}: {}".format(
            "open" if self.state_open
            else "undefined" if self.state_open is None
            else "closed",
            self.state_ext_open_detail))

        # set led
        led = None
        if self.state_ext_open_detail == state_chooser_button.ESTATE_OPEN_FOR_PUBLIC:
            led = LED_OPEN_PUBLIC
        elif self.state_ext_open_detail == state_chooser_button.ESTATE_OPEN_FOR_MEMBERS:
            led = LED_OPEN_MEMBERS
        elif self.state_ext_open_detail == state_chooser_button.ESTATE_CLOSED:
            led = LED_CLOSED
        self.serial_communicator.set_led(led)

        if self.timer:
            self.timer.cancel()
        self.timer = Timer(PUBLIC_DEBOUNCE_SECS, self._set_public_state)
        self.timer.start()

    def _set_public_state(self):
        if self.state_open == self.public_state_open and \
                self.state_ext_open_detail == self.public_state_ext_open_detail:
            return
        self.public_state_last_change = self.state_last_change
        self.public_state_open = self.state_open
        self.public_state_ext_open_detail = self.state_ext_open_detail
        self._logger.info("public state changed to {}: {}".format(
            "open" if self.state_open
            else "undefined" if self.state_open is None
            else "closed",
            self.state_ext_open_detail))

        message = state_chooser_button.message_by_state(
            self.public_state_ext_open_detail)

        for publisher in self.publishers:
            publisher.publish(
                is_open=self.public_state_open,
                open_detail=self.public_state_ext_open_detail,
                message=message,
                last_change_time=self.public_state_last_change)

    def on_button_changed(self, sender):
        """
        @type sender: state_chooser_button.StateChooserButton
        """
        self._logger.info("button pressed: {}".format(sender.ext_state))
        self._set_state(sender.ext_state)

    def run(self):
        self.d_main.on_change.connect(self.on_main_door_changed)
        self.button.on_change.connect(self.on_button_changed)
        self.serial_communicator.run()


if __name__ == '__main__':
    logging.basicConfig(
        format='[%(asctime)s] %(levelname)s: %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO)
    d = Dvarapala()
    d.run()
