import calendar
import logging

import homie  # https://github.com/jalmeroth/homie-python

from config import MQTT_HOMIE_ENABLE

logger = logging.getLogger(__name__)

my_homie = homie.Homie("homie-config.json")
node_state = my_homie.Node("state", "space_state")

my_homie.setFirmware("dvarapala", "1.0.0")
my_homie.setup()


def publish(is_open, open_detail, message, last_change_time):
    if not MQTT_HOMIE_ENABLE:
        return

    logger.info("publishing MQTT")

    my_homie.setNodeProperty(
        node_state, "open",
        "null" if is_open is None else str(is_open).lower(),
        retain=True)
    my_homie.setNodeProperty(
        node_state,
        "open_detail",
        open_detail,
        retain=True)
    my_homie.setNodeProperty(
        node_state,
        "message",
        message,
        retain=True)
    my_homie.setNodeProperty(
        node_state,
        "lastchange",
        calendar.timegm(last_change_time.timetuple()),
        retain=True)
