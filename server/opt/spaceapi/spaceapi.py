#!/usr/bin/env python

import json
import logging
from threading import Timer
import signal

import paho.mqtt.client as mqtt

from config import MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE, MQTT_TOPIC, \
    BASE_JSON_PATH, DEST_PATH

if not MQTT_TOPIC.endswith("/"):
    MQTT_TOPIC += "/"

TOPIC_ONLINE = MQTT_TOPIC + "$online"
TOPIC_OPEN = MQTT_TOPIC + "state/open"
TOPIC_OPEN_DETAIL = MQTT_TOPIC + "state/open_detail"
TOPIC_MESSAGE = MQTT_TOPIC + "state/message"
TOPIC_LASTCHANGE = MQTT_TOPIC + "state/lastchange"

space_is_online = False
space_open = None
space_open_detail = None
space_message = None
space_lastchange = None

debounce_timer = None

DEBOUNCE_TIME = 5

logger = logging.getLogger(__name__)


def on_client_connect(client, userdata, flags, rc):
    logger.info("Connected with result code {}".format(rc))

    client.subscribe(TOPIC_ONLINE)
    client.subscribe(TOPIC_OPEN)
    client.subscribe(TOPIC_OPEN_DETAIL)
    client.subscribe(TOPIC_MESSAGE)
    client.subscribe(TOPIC_LASTCHANGE)


def on_client_disconnect(client, userdata, rc):
    logger.info("Disconnected with result code {}".format(rc))

    global space_is_online
    space_is_online = False

    write_spaceapi_json()


def on_client_message(client, userdata, msg):
    logger.debug(msg.topic+" "+str(msg.payload))

    if msg.topic == TOPIC_ONLINE:
        on_space_online_change(msg.payload)
    elif msg.topic == TOPIC_OPEN:
        on_space_open_change(msg.payload)
    elif msg.topic == TOPIC_OPEN_DETAIL:
        on_space_open_detail_change(msg.payload)
    elif msg.topic == TOPIC_MESSAGE:
        on_space_message_change(msg.payload)
    elif msg.topic == TOPIC_LASTCHANGE:
        on_space_lastchange_change(msg.payload)
    else:
        logger.error("unknown topic: {}".format(msg.topic))


def update_spaceapi_json():
    global debounce_timer
    if debounce_timer:
        debounce_timer.cancel()
    debounce_timer = Timer(DEBOUNCE_TIME, write_spaceapi_json)
    debounce_timer.start()


def write_spaceapi_json():
    logger.info("writing json")
    with open(BASE_JSON_PATH, "r") as f:
        j = json.load(f)
    if space_is_online and None not in [space_open, space_open_detail,
                                        space_message, space_lastchange]:
        j["state"]["ext_open_detail"] = space_open_detail
        j["state"]["lastchange"] = space_lastchange
        j["state"]["message"] = space_message
        j["state"]["open"] = space_open
    else:
        logger.warning("state is undefined")
    with open(DEST_PATH, "w") as f:
        json.dump(j, f, indent=4, separators=(',', ': '))


def on_space_online_change(payload):
    online = payload == "true"
    global space_is_online
    if space_is_online == online:
        return
    space_is_online = online
    update_spaceapi_json()


def on_space_open_change(payload):
    global space_open
    is_open = payload if payload in ["true", "false", "null"] else None
    if space_open == is_open:
        return
    space_open = is_open
    update_spaceapi_json()


def on_space_open_detail_change(payload):
    global space_open_detail
    open_detail = payload if payload in [
        "open_for_members", "open_for_public", "closed", "unknown"] else None
    if space_open_detail == open_detail:
        return
    space_open_detail = open_detail
    update_spaceapi_json()


def on_space_message_change(payload):
    global space_message
    message = payload
    if space_message == message:
        return
    space_message = message
    update_spaceapi_json()


def on_space_lastchange_change(payload):
    global space_lastchange
    try:
        lastchange = int(payload)
    except:
        lastchange = None
    if space_lastchange == lastchange:
        return
    space_lastchange = lastchange
    update_spaceapi_json()


if __name__ == '__main__':
    logging.basicConfig(
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO)

    write_spaceapi_json()

    client = mqtt.Client()
    client.on_connect = on_client_connect
    client.on_message = on_client_message
    client.on_disconnect = on_client_disconnect

    def on_quit(signum, stack):
        logger.info("quitting...")
        client.disconnect()

    signal.signal(signal.SIGTERM, on_quit)

    try:
        client.connect_async(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)

        client.loop_forever(retry_first_connection=True)
    except KeyboardInterrupt:
        on_quit(None, None)
