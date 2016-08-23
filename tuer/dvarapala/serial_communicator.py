
from time import sleep
import serial
import logging
import json
import door_state
import state_chooser_button
from threading import Event

from config import SERIAL_PORT, SERIAL_BAUD

LED_OPEN_PUBLIC = "led_open_public"
LED_OPEN_MEMBERS = "led_open_members"
LED_CLOSED = "led_closed"


class SerialCommunicator(object):

    def __init__(self, door_main, door_kitchen, door_lounge, door_back, button):
        """
        @type door_main: door_state.DoorState
        @type door_kitchen: door_state.DoorState
        @type door_lounge: door_state.DoorState
        @type door_back: door_state.DoorState
        @type button: state_chooser_button.StateChooserButton
        """
        self._logger = logging.getLogger(__name__)

        self.door_main = door_main
        self.door_kitchen = door_kitchen
        self.door_lounge = door_lounge
        self.door_back = door_back
        self.button = button

        self._uc_connection = None
        self._commands = []
        self._run_delay_event = Event()

    def _initialize_serial(self):
        self._logger.info("initializing serial")
        self._uc_connection = serial.Serial(SERIAL_PORT,
                                            SERIAL_BAUD,
                                            timeout=3)
        sleep(2)  # let the arduino initialize itself
        self._uc_connection.flushInput()

    def set_led(self, led):
        if led not in [LED_OPEN_PUBLIC, LED_OPEN_MEMBERS, LED_CLOSED, None]:
            self._logger.error("unknown led: {}".format(led))
            return
        if not led:
            self._commands.append("turn leds off")
        else:
            self._commands.append("turn {} on".format(led))
        self._run_delay_event.set()

    @staticmethod
    def _json_answer_is_valid(answer):
        valid_states = ["UNDEFINED", "OPEN", "CLOSED"]
        try:
            valid = True
            valid = valid and answer["1"] in valid_states
            valid = valid and answer["2"] in valid_states
            valid = valid and answer["3"] in valid_states
            valid = valid and answer["4"] in valid_states
            valid = valid and "btn_pressed" in answer
        except KeyError:
            valid = False
        return valid

    def _process_answer(self, answer_json):
        self.door_kitchen.state = door_state.STATE_UNLOCKED if answer_json["1"] == "OPEN" else door_state.STATE_LOCKED if answer_json["1"] == "CLOSED" else door_state.STATE_UNDEFINED
        self.door_lounge.state = door_state.STATE_UNLOCKED if answer_json["2"] == "OPEN" else door_state.STATE_LOCKED if answer_json["2"] == "CLOSED" else door_state.STATE_UNDEFINED
        self.door_back.state = door_state.STATE_UNLOCKED if answer_json["3"] == "OPEN" else door_state.STATE_LOCKED if answer_json["3"] == "CLOSED" else door_state.STATE_UNDEFINED
        self.door_main.state = door_state.STATE_UNLOCKED if answer_json["4"] == "OPEN" else door_state.STATE_LOCKED if answer_json["4"] == "CLOSED" else door_state.STATE_UNDEFINED
        if answer_json["btn_pressed"] != "":
            self.button.ext_state = state_chooser_button.ESTATE_OPEN_FOR_PUBLIC if answer_json["btn_pressed"] == "open_for_public" else state_chooser_button.ESTATE_OPEN_FOR_MEMBERS if answer_json["btn_pressed"] == "open_for_members" else state_chooser_button.ESTATE_CLOSED if answer_json["btn_pressed"] == "closed" else state_chooser_button.ESTATE_UNDEFINED

    def run(self):
        while True:
            try:
                self._initialize_serial()
            except:
                self._logger.error("initializing serial failed. retry in 5s")
                sleep(5)
                continue
            try:
                while True:
                    # write commands in queue
                    if self._commands:
                        self._logger.debug("writing: \"{}\\n\"".format(
                            self._commands[0]))
                        self._uc_connection.write("{}\n".format(self._commands[0]))
                        del self._commands[0]

                    # get sensors
                    self._logger.debug("writing: \"get sensors\\n\"")
                    self._uc_connection.write("get sensors\n")
                    answer = self._uc_connection.readline().replace("\n", "").replace("\r", "")
                    self._logger.debug("received: {}".format(answer))
                    answer_json = json.loads(answer)

                    if not self._json_answer_is_valid(answer_json):
                        raise Exception("answer is invalid")

                    self._process_answer(answer_json)

                    self._run_delay_event.wait(0.2)
                    self._run_delay_event.clear()
            except KeyboardInterrupt:
                self._logger.info("KeyboardInterrupt. Quit.")
                self._uc_connection.close()
                break
            except:
                self._logger.error("error occurred. restarting serial.")
