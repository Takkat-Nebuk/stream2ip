#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Einstellungen für
#
# stream2ip
# version = '0.3.0'
# Bitte die Variablennamen unverändert lassen
# und die Leerzeichen belassen
#
# stream2ip GUI Text German
Intro_Text = '''<span size="x-large"><b>stream2ip</b></span>
'''
State_Connected = ' verbunden mit: '
State_Searching = 'Suche  '
State_Disconnected = 'Getrennt'
State_Notfound = ''' <span color="red"> wurde nicht verbunden!</span>
'''
State_Reset = "<b>PulseAudio wurde zurückgesetzt</b>"
State_Error_Disconnect = '''<b><span color="red">Fehler:</span></b>
Wir dürfen die Verbindung nicht trennen.
'''
State_Checkinstall = 'Überprüfe installierte Pakete'
State_Install_ok = 'Ok'
State_Nopackage = '''<span color="red">Die folgenden Pakete müssen
noch installiert werden:</span>
'''
State_Wait = '''<span color="red">Einen Moment bitte... </span>'''
Connect = 'Verbinden'
Disconnect = 'Trennen'
Stop = 'Abbrechen'
Quit = 'Beenden'
Show = 'Zeige Fenster'

# Text für s2ip_setup <- aus glade-file
sbutton_txt = 'Ok'
qbutton_txt = 'Abbruch'
soq_button_txt = 'IP-Einstellungen sichern'
cos_button_txt = 'Automatisch verbinden'
min_button_txt = 'Nach dem Verbinden minimieren'
doq_button_txt = 'Beim Programmende trennen'
sqoptions_txt = '<u>Start/Ende-Optionen</u>'
dev_label_txt = '<b>Geräte</b>'

ip_label_txt = [
'IP der AirPort Express:', 
'MAC des Bluetooth-Geräts:', 
'Verzeichnispfad:',
'Keine Optionen verfügbar',
'Konfiguration/Playlist:',
'Auszuführender Code:'
]

Err_Msg = [
'''Mit <b>"Verbinden"</b> wird die Verbindung
zum Gerät hergestellt.''', # 0 kein Fehler
'''Das angegebene Gerät antwortet nicht.
<i>Ist die Konfiguration richtig?
Ist das Gerät eingeschaltet?</i>''', # 1 Ping Fehler
'''Mindestens ein benötigtes Software-
Paket konnte nicht gefunden werden.''', # 2 Paket fehlt
'''Das aufgerufenen Programm konnte
die Verbindung nicht herstellen.''', # 3 Subprocess Fehler
'''Datei nicht vorhanden.''', # 4 File not found
'''Musikplayer läuft noch.
Bitte stoppen''' # 5 Player running
]

