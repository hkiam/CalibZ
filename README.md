# CalibZ
Python-Script zum Konfigurieren des Z-Offsets für das Auto-Leveling bei 3d Druckern.

Anleitung:
0. Vorbereitungen
   pySerial installieren: 
	https://pyserial.readthedocs.io/en/latest/pyserial.html
   

1. im Kopf des Scripts 'CalibZ.py' eigene Parameter eintragen, z.B.
	serialPort = 'COM5'		# COM5
	xoffset = 70			# Abstand zwichen Düse und Sensor auf der X-Achse
	extruderTemp = 205		# Temperaturen während der Einstellung
	bedTemp = 60
2. Script 'CalibZ.py' starten
	python CalibZ.py

3. Den Anweisungen in der Konsole folgen.



useful script to adjust the z-offset for auto-leveling on 3d printers

TODO