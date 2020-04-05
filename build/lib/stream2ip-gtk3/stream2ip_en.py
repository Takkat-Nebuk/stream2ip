#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Setup file for 
#
# stream2ip
# version='1.1.6'
# please don't change variable names
# and keep spaces
#
# Menutext English
Intro_Text = '''<span size="x-large"><b>stream2ip</b></span>
'''
State_Connected = ' connected to: '
State_Searching = 'Searching: '
State_Disconnected = 'Disconnected'
State_Notfound = ''' <span color="red"> not connected!</span>
'''
State_Reset = "<b>PulseAudio resetted</b>"
State_Error_Disconnect = '''<b><span color="red">Error:</span></b>
We are not allowed to disconnect:
'''
State_Checkinstall = 'Checking installed packages'
State_Install_ok = 'Ok'
State_Nopackage = '''<span color="red">Please install the following
packages:</span>
'''
State_Wait = '''<span color="red">One moment, please... </span>'''
Connect = 'Connect'
Disconnect = 'Disconnect'
Stop = 'Stop'
Quit = 'Quit'
Show = 'Show'

ip_label_txt = [
'', 
'',
'Path to Directory:',
'',
'Configuration/Playlist:',
'',
''
]

Err_Msg = [
'''Press <b>"Connect"</b> to establish
a connection with device above.''', #0 no error
'''Above Device is not responding.''', #1 ping error
'''Missing software package(s).''', #2 package error
'''Error with subprocess.''', #3 subprocess error
'''File not found.''', # 4
'''Please stop player first'''# 5 Player running
]


# Text for s2ip_setup from glade-file

sbutton_txt = 'Ok'
qbutton_txt = 'Cancel'
soq_button_txt = 'Save IP settings on quit'
cos_button_txt = 'Connect on startup'
min_button_txt = 'Minimize on connection'
doq_button_txt = 'Disconnect on quit'
sqoptions_txt = '<u>Startup/Quit Options</u>'

dev_label_txt = '<b>Devices</b>'


