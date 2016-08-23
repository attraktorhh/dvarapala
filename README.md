# Dvarapala

Türstatus im Attraktor e. V.

## Der Name

https://de.wikipedia.org/wiki/Dvarapala

## Die Funktionsweise

1. je ein (Wechsel-)Taster an den 4 Türen wird gedrückt, wenn die Tür abgeschlossen ist
2. Platine mit diskreter Logik (macht TTL-Signale und stellt Fehler fest)
3. Arduino (macht Serielle)
4. Raspberry PI
	* Veröffentlicht den Status
		* auf [Twitter](https://twitter.com/tuerstatus)
		* per MQTT im [Homie-Format](https://github.com/marvinroger/homie)
5. auf dem Server läuft ein MQTT-Client, veröffentlicht Status [im SpaceAPI-Format](http://spaceapi.net/) auf der [Website](https://blog.attraktor.org/spaceapi/spaceapi.json)

Der Status wechselt automatisch von "Geschlossen" auf "Offen für Mitglieder", wenn die Haupteingangstür aufgeschlossen wird und auf "Geschlossen", wenn sie abgeschlossen wird. Er kann außerdem manuell am Panel am Eingang eingestellt werden. Der Status wird debounced (z. B. 5 Min).

1-3 könnte in Zukunft durch ESP2866 direkt an den Türen ersetzt werden, 5V-Leitung liegt.

## FAQ

https://blog.attraktor.org/tuerstatus-faq/