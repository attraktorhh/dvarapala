# coding=utf-8

PUBLIC_DEBOUNCE_SECS = 5 * 60

SERIAL_PORT = "/dev/ttyACM0"
SERIAL_BAUD = 19200

MESSAGE_OPEN_FOR_PUBLIC = "Offen - komm' vorbei!"
MESSAGE_OPEN_FOR_MEMBERS = "Offen fuer Mitglieder"
MESSAGE_CLOSED = "Geschlossen"
MESSAGE_UNDEFINED = "Unbekannt"

TWITTER_ENABLE = False
TWITTER_ACCESS_TOKEN_KEY = ""
TWITTER_ACCESS_TOKEN_SECRET = ""
TWITTER_CONSUMER_KEY = ""
TWITTER_CONSUMER_SECRET = ""
TWITTER_MESSAGE = "{message} [seit %d.%m.%Y %H:%M]"

MQTT_HOMIE_ENABLE = False
# MQTT config: homie-config.json