#!/usr/bin/python3
#-*- coding: utf-8 -*-
#
# stream2ip
# Author: Takkat Nebuk
# Date: 2020-04-03
version = '1.1.6'
#####################################################################################
# Copyright (C) 2020 Takkat Nebuk                                                   #
#                                                                                   #
# This program is free software; you can redistribute it and/or modify it under the #
# terms of the GNU General Public License as published by the Free Software         #
# Foundation; either version 3 of the License, or any later version.                #
#                                                                                   #
# This program is distributed in the hope that it will be useful, but WITHOUT ANY   #
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A   #
# PARTICULAR PURPOSE. See the GNU General Public License for more details.          #
#                                                                                   #
# You should have received a copy of the GNU General Public License along with this #
# program; if not, see http://www.gnu.org/licenses/                                 #
#####################################################################################
import os
import time
import sys

### python3 depends: python3-gi, python3-dbus, python3-apt

try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, GdkPixbuf, GLib
    from gi.repository import GObject
    GLib.set_prgname('stream2ip')  ## needed for wayland
except:
    exit('<E> GI Library not found.')

import subprocess
import s2ip_setup
import shutil
#
from helptext import * ## load help text to GUI

try:
    import dbus
except:
    exit('DBus bindings not found. Please install python3-dbus')

if sys.version >= '3': ## we are on Python >= 3.0
    import urllib.request, urllib.error, urllib.parse
else: ## we are on Python >= 2.7
    print('<W> Running stream2ip on Python2 is not recommended')
    import urllib, urllib2

################### we depend on python-mutagen to read metatags from mp3 files #####
try: ############## for displaying artist/title on Ices playlist streams only #######
    from mutagen.mp3 import MP3
    from mutagen.easyid3 import EasyID3
    pymutagen = True
except:
    print ('<W> Python mutagen module not available')
    pymutagen = False

runpath = os.path.dirname(os.path.realpath(__file__)) + '/'
homepath = os.path.expanduser('~') + '/.config/stream2ip/'
defaults = s2ip_setup.load_defaults(homepath) # load default settings
#
# Here's some init stuff:
lang = os.getenv("LANG")
spoken = lang.split("_") # returns spoken[language, coding]
if spoken[0] == 'de': # speak German?
    from stream2ip_de import *
else: # if not then maybe English
    from stream2ip_en import *
#
# Parse CLI Options
cli_options = sys.argv
for opts in cli_options:
    if opts == '-v' or opts == '-V' or opts == '--verbous':
        verbous = True
    else:
        verbous = False
    if opts == '-l' or opts == '-L' or opts == '--log':
        logfile = True
    else:
        logfile = False
    if opts == '?' or opts == '-?' or opts == 'help' or opts == '-help':
        subprocess.Popen('man stream2ip', shell = True)
        exit(0)
    if opts == '-s' or opts == '-S' or opts == '--setup':
        if sys.version >= '3':
            subprocess.call(['python3', runpath + 's2ip_setup.py'])
        else:
            subprocess.call(['python', runpath + 's2ip_setup.py'])
        sys.exit(0)
#
# Beautiful Icons
Icon = runpath + 'icons/S2-x.svg' # default/grey
Icon_orange = runpath + 'icons/S2-y.svg' # orange
Icon_green = runpath + 'icons/S2-g.svg' # green
Icon_blue = runpath + 'icons/S2-b.svg' # blue
Icon_red = runpath + 'icons/S2-r.svg' # red
Icon_black = runpath + 'icons/S2-c.svg' #black
Icon_Attention = runpath + 'icons/S2-att.svg' # Attention
Current_Icon = Icon
# print(Icon)
# Panel Icons
pIcon = runpath + 'icons/S2-x24.svg' # default/grey
pIcon_o = runpath + 'icons/S2-y24.svg' # orange
pIcon_g = runpath + 'icons/S2-g24.svg' # green
pIcon_b = runpath + 'icons/S2-b24.svg' # blue
pIcon_r = runpath + 'icons/S2-r24.svg' # red = green
pIcon_k = runpath + 'icons/S2-c24.svg' #black
pIcon_Att = runpath + 'icons/s2-att24.svg' # Attention
#
# Setup defaults and globals
# defaults = ['5', #0 Device (pos in list below)
#'xxx.xxx.xxx.xxx', #1 IP of AirportExpress
#'XX:XX:XX:XX:XX:XX', #2 MAC of Bluetooth device
#'/path/music', #3 Path for UPnP Shares
#'DLNA-live device', #4
#'filename', #5 playlist or config files for Ices, Ices2, Darkice
#'OS command', #6 OS Commands
#'N', #7 save on quit
#'N', #8 connect on start
#'N', #9 minimize
#'Y', #10 disconnect on quit
#'N', #11 no setup button
#'',  #12 command to run on connection
#'4', #13 Bluetooth timeout
#'0', #14 Media player for tags
#'admin', #15 Icecast admin name
#'hackme', #16 Icecast admin password
#'N', #17 Add to Startup Applications
#'N'] #18 Run media player on connect
#
devices = [
'None',
'None',
'UPnP-Device',
'DLNA live',
'RTP/Multicast',
'Internet Radio',
'None']
# Globals
default_sink = ''
PA_Device = ''
pamodul = 0 # we dont have a pulse module yet
connected = False # we are not yet connected
err = 0 # no error so far
timeloop = 0 # gobject timer
CheckLoop = True # quit gtk timer loop when False
ConnectLoop = False # gtk timer loops forever but does nothing if False
isloop = False #loop flag
timeout = 0
ushare = ''
icecast2 = ''
icecast = ''
ices2 = ''
icepid = 0
coverart = "/cover.jpg" #change if different!
metadata = ''
IceServer = '' ## whether icecast or icecast2
IceSystemwide = 0
IceCredentials = [
'', #IceAdmin = ''
'', #IcePass = ''
'', #IceIP = ''
'', #IcePort = ''
''#IceMount = ''
]
mplayers = s2ip_setup.mplayers
playerstate = 'None' # 'Playing' 'Paused' 'Stopped'
ice_mount = ''
mpris_v = 0 # MPRIS version 1.0 or 2.0 for control_play
runcommand = True # we only run this command once
runplayer = True # we only start the player once
use_appind = defaults[11]=='N'
if not use_appind:
    print('<I> Application Indicators disabled - run setup to enable')
DLNA_ip = ''


###########################################
# Here we go with button actions from gtk:#
###########################################
def on_button_clicked(buttonid, event):
    global defaults, devices, pamodul, connected, homepath, CheckLoop, ConnectLoop, timeout, PA_Device, mplayers
    pos = int(defaults[0])
    PA_Device = devices[pos]
    status.set_label('')
    defaults[pos+1] = entrybox.get_text() # in case edited
    window.present()
    player = mplayers[int(defaults[14])]
    if buttonid == hbutton:  ## we call for help
        help_window.show()
    elif buttonid == help_quit:
        help_window.hide()
    elif buttonid == help_online: # we call online help
        run_command('xdg-open http://stream2ip.takkat.de &')
#        run_command('xdg-open ' + runpath + '/docs/html/Manual.html &')
    elif buttonid == ffwdbutton: # Skip to next track
        if connected:
            if ('.m3u' in defaults[5] and PA_Device == 'Internet Radio'): #playlist on Ices
                run_command('kill -usr1 ' + str(pamodul))
            elif getpid(player['prgname']): # the player is running
                control_player(player, 'next')
    elif buttonid == fcbutton: # Filechooser
        filename = ''
        if connected:
            connected = disconnect(PA_Device)
        if pos == 2: #UPnP needs folders
            filename = s2ip_setup.f_choose('Folder')
            print('Fetched Folder ', filename)
        if pos == 5: #Icecast needs a file
            filename = s2ip_setup.f_choose('File')
        if pos == 3: # choose DLNA renderer
            filename = s2ip_setup.f_choose('Setup')
        if filename:
            entrybox.set_text(filename)
        defaults[pos+1] = entrybox.get_text() # in case edited
    elif buttonid == cbutton: #Connect/Disconnect
        if not connected:
            debug_print('Going to connect: ' + PA_Device)
            status.set_label(State_Searching + PA_Device)
            connected = connect(defaults)
            if not connected:
                debug_print('<E> Connection failed. Device: '+ PA_Device)
            device_ready(pamodul)
            if timeout:
                ConnectLoop = True
        else:
            debug_print('Going to disconnect: ' +PA_Device)
            ConnectLoop = False
            connected = disconnect(PA_Device)
    elif buttonid == qbutton: #Quit
        save_quit(None, None)
    elif buttonid == sbutton: # we like to setup
        if connected:
            connected = disconnect(PA_Device)
        debug_print('Starting setup program ...')
        s2ip_setup.save_defaults(defaults, homepath) #otherwise changes lost
        if sys.version >= '3':
            subprocess.call(['python3', runpath + 's2ip_setup.py'])
        else:
            subprocess.call(['python', runpath + 's2ip_setup.py'])
        defaults = s2ip_setup.load_defaults(homepath)
        debug_print('Defaults changed to: ' + str(defaults))
        pos = int(defaults[0])
        if pos == 6 or pos == 4: #################################
            entrybox.hide()
            entrybox.set_text('')
        else:
            entrybox.show()
            entrybox.set_text(defaults[pos+1])
        PA_Device = devices[pos]
        timeout = defaults[13]
        if timeout:
            ConnectLoop = True
        if defaults[8] == 'Y': # Autoconnect
            connected = connect(defaults)
        dlabel.set_label('<b>' + PA_Device + ':</b>')
        device_ready(pamodul)
    else: # Reset Sound Server
        pamodul = 0
        connected = ResetServer()
    return


def connect(settings):
    global pamodul, timeout, isloop, ConnectLoop, runpath, icepid, runcommand
    pos = int(settings[0]) + 1
    timeout = int(settings[13]) #13 start loop for device detection
    pamodul = False
    if pos == 7: #PA_Device == 'None': Shell commands disabled on >1.0.0
        pamodul = 'None'
        timeout = 0 # we don't loop
    elif pos == 3: #PA_Device == 'UPnP-Device':
        pamodul = UPNP_connect(settings[pos])
        timeout = 0 # we don't loop
#    elif pos == 1: #PA_Device == 'AirPort Express': deprecated
#        pamodul = AE_connect(settings[pos])
#    elif pos == 2: #PA_Device == 'Bluetooth': deprecated
#        pamodul = BLUE_connect(settings[pos])
    elif pos == 4: ##PA_Device == 'DLNA live':
        pamodul = DLNA_connect(settings[pos])
    elif pos == 5: #PA_Device == 'RTP/Multicast':
        pamodul = RTP_connect()
    elif pos == 6: #PA_Device == 'Internet Radio':
        pamodul = Ice_connect(settings[pos])
        icepid = pamodul
    if timeout:
        ConnectLoop = True
    if not isloop: #only start loop once!
        connect_loop(timeout)
    if not pamodul:
        return False
    else:
        if settings[12] and runcommand:# run command after connect
            runcommand = False # but only do that once
            run_command(settings[12])
        return True


def connect_loop(timeout):
    global timeloop, isloop
    if timeout: # don't loop if we don't want this
        debug_print('Connecting time loop: ' + str(timeout) + ' seconds')
        isloop = True
        timeloop = GLib.timeout_add_seconds(timeout, on_timeout, False)
    return


def on_timeout(options): #what to check when looping
    global defaults, mplayers, pamodul, metadata, CheckLoop, ConnectLoop, connected, isloop, icepid, status, pamodul, PA_Device, Current_Icon, runcommand, runplayer, DLNA_ip
    playerpid = 0
    if not ConnectLoop: # do nothing
        return True
    pos = int(defaults[0]) + 1
    mp_i = int(defaults[14])
    if connected: #check if all devices are still alive and maybe get Tags
        if pos == 4: # 'DLNA live' ## using pulseaudio-dlna
            if not DLNA_search(DLNA_ip):
                connected = disconnect('DLNA live')
                return CheckLoop
        if 'm3u' in defaults[pos]:# we are doing playlists
            path_played = ice_nowplaying()
            if path_played:
                newmetadata = get_tags_from_file(path_played)
                if newmetadata != metadata:
                    metadata = newmetadata
                    track_changed(metadata)
            else:
                debug_print('<W> EOF or Error in playlist: ' + defaults[pos])
                ConnectLoop = False
                connected = disconnect('Internet Radio')
            return CheckLoop
        if not mp_i: # we don't care about metatags
            return CheckLoop
        playerpid = getpid(mplayers[mp_i]['prgname'])
        if not playerpid: # player is not running
            if defaults[18] == 'Y' and runplayer:
                run_command(mplayers[mp_i]['prgname'])
                runplayer = False
            else:
                status.set_label(State_Searching + mplayers[mp_i]['name'])
        else:
            if mplayers[mp_i]['mprispath'] == '/Player': # we are on MPRIS 1.0
                newmetadata = get_metadata(mplayers[mp_i])
            else:
                newmetadata = get_metadata2(mplayers[mp_i]) # for MPRIS 2.0
            if newmetadata != metadata: #act only if changed
                metadata = newmetadata
                track_changed(metadata)
        return CheckLoop
    else: # we're not connected
        if defaults[8] == 'N': # we may not want to autoconnect either
            ConnectLoop = False
            return CheckLoop
        Icon_layout('orange')
        Current_Icon = Icon_orange
        status.set_label(State_Searching + PA_Device)
        if pos == 4: #PA_Device == 'DLNA live' -> needs loop!
            pamodul = DLNA_connect(defaults[pos])
        elif pos == 5: #PA_Device == 'RTP/Multicast'
            pamodul = RTP_connect()
        elif pos == 6: #PA_Device == 'Internet Radio'
            pamodul = Ice_connect(defaults[pos])
            icepid = pamodul
        else:
            ConnectLoop = False # no Looping allowed
            CheckLoop = False
        if pamodul:
            connected = True
            if runcommand and defaults[12]: # run command after connect
                runcommand = False # but only do that once
                run_command(defaults[12])
            device_ready(pamodul)
            debug_print(PA_Device +' connected to ' + defaults[pos])
        else:
            connected = False
    return CheckLoop # when True continue loop until False


def getpid(program):
    if not program:
        return 0
    args = ['ps', 'o', 'pid', '--no-headers', '-C', program]
    output = subprocess.Popen(args, stdout=subprocess.PIPE)
    pid = output.communicate()[0].decode().replace('\n', '')
    if pid:
        return int(pid.split()[0]) # Warning! Only first pid is used.
    else:
        return 0


def paversion(): # we need to know if we are running pa 0.9.x or 1.0.x
    args = ['pacmd list-modules | grep -m 1 module.version'] # only 1st module
    retcode = subprocess.Popen(args, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    status = retcode.communicate()
    debug_print(status)
    version = status[0].decode().split('= "')[1].split('"')[0]
    version = str(version).replace("\n", '')
    debug_print('Pulseaudio version: ' + version)
    return version




def UPNP_connect(path):
    global err
    global ushare
    if path == 'minidlna':
        pid = minidlna_connect()
        return str(pid)
    allpaths=path.split(' ')
    path = ''
    status = ['']
    for i in range(len(allpaths)):
        if not os.path.isdir(allpaths[i]): # wrong path
            print('<E> ' + allpaths[i] + ' does not exist')
            err = 4
            return 0
        path = path + " -c " + allpaths[i]
    args = ["ushare -D --name=stream2ip " + path]
    try:
        pid = str(subprocess.Popen(args, shell = True).pid)
    except:
       debug_print(sys.exc_info())
       err = 2
       print('<E> ushare not found! ==> Install <ushare>')
       return 0
    if not status[0]:
        err = 0
        debug_print('UPnP/uShare connected for: ' + path + 'PID: ' + pid)
        return str(pid) #'uShare'
    else:
        err = 3
        debug_print('<E> failed to setup uShare for: ' + path)
        return 0


def minidlna_connect():
    global homepath
    if not shutil.which("minidlna"):
        messagebox(Gtk.MessageType.ERROR, 'MiniDLNA not found','Please install package <b>minidlna</b>')
        return ''
    pid = getpid('minidlna') ## whether MiniDLNA is running system-wide
    if pid:
        debug_print('<W> minidlna is already running')
        return pid
    configfile = homepath + 'minidlna.conf'
    if not os.path.isfile(configfile):
        try:
            shutil.copy('/etc/minidlna.conf', homepath)
        except:
            messagebox(Gtk.MessageType.ERROR, 'MiniDLNA configuration not found','Was minidlna installed?')
        messagebox(Gtk.MessageType.INFO, 'MiniDLNA configuration copied','Please edit the following file to\ndefine paths to your media library:\n\n'+ configfile)
    pid = subprocess.Popen(['minidlna', '-f', configfile, '-P', homepath+'minidlna.pid']).pid
    return str(pid)


def DLNA_connect(renderpath):
    global pamodul, verbous, ConnectLoop, timeout, DLNA_ip, homepath
    if not shutil.which("pulseaudio-dlna"):
	    messagebox(Gtk.MessageType.ERROR, 'Pulseaudio_DLNA not found','Please install package <b>pulseaudio-dlna</b>')
	    return ''
    pid = getpid('pulseaudio-dlna')
    if pid:
        debug_print('<E>pulseaudo-dlna was already running - trying to restart...')
        pamodul = 0
        disconnect('DLNA live')
    lastsink = get_sink()[3]
    padlnacfg = []
    if os.path.isfile(homepath + 'padlna.cfg'):
        with open(homepath + 'padlna.cfg', 'r') as f: # load settings from file
            text = f.read()
            padlnacfg = text.rstrip('\n').split(" ")
        f.close()
        debug_print('<I> Using config file for pulseaudio-dlna')
        debug_print(padlnacfg)
    if not renderpath: ## no options given, use only defaults
        debug_print('<W> No options for DLNA live given. Using padlna.cfg file or defaults.')
        ConnectLoop = False # we can't loop then
        timeout = 0
        args = ['pulseaudio-dlna'] + padlnacfg
    elif renderpath[0:7] == 'http://': ## use defaults except renderer
        args = ['pulseaudio-dlna','--renderer-urls', renderpath] + padlnacfg
        DLNA_ip = renderpath.rsplit('http://', 1)[1].split(':')[0].split(' ')[0]
        debug_print('<I> DLNA live using --renderer-urls ' + renderpath)
    elif '--' in renderpath[0:2]:  ## guess we had all options given
        debug_print('<I> DLNA live using CLI options for pulseaudio-dlna')
        if not '--renderer-urls' in renderpath:
            debug_print('<W> DLNA live can not find an URL for autoconnecting')
            ConnectLoop = False ## we can't loop
            timeout = 0
        else:
            DLNA_ip = renderpath.split('--renderer-urls ',1)[1].split(' ',1)[0]
        args = ['pulseaudio-dlna'] + renderpath.split(' ')
    elif '@' in renderpath: ## arguments were given as 'rendername@ip'
        debug_print('<I> DLNA live using ' + renderpath + ' to connect')
        args = ['pulseaudio-dlna', '--filter-device', renderpath.split('@')[0]] + padlnacfg
        DLNA_ip = renderpath.split('@')[1]
    else:
        print ('<E> Bad arguments for DLNA live. Please run setup')
        err = 1
        return 0
    if DLNA_ip:
        if not DLNA_search(DLNA_ip): ## no renderer
            err = 1
            print ('Renderer not found')
            return 0
    time.sleep(1) ## give lazy renderers some time
    try:
        debug_print("<I> Connecting pulseaudio-dlna with " + renderpath)
        if verbous: ## we may want to read pulseaudio-dlna output
            subprocess.Popen(args)
        else:
            subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pid = getpid('pulseaudio-dlna') ## get PID
        debug_print('Pulseaudio-dlna PID:' + str(pid))
    except:
        debug_print(sys.exc_info())
        err = 1
        return 0
    newsink = get_sink()[3]
    countdown = 15 ## timeout to wait for sink to be established
    debug_print('Waiting for sink to be established')
    while newsink == lastsink:
        time.sleep(1)
        newsink = get_sink()[3]
        countdown -= 1
        if not countdown:
            debug_print('<E>Switching to DLNA-sink failed')
            return ''
    newsink = get_sink()[3] ## assuming last added sink is DLNA sink
    debug_print('Setting sink to index '+ newsink)
    set_sink(newsink)
    return str(pid)


def DLNA_search(ip):
    global err
    if subprocess.call("ping -c 1 -W 1 "+ ip + " >/dev/null", shell=True):
        err = 0
        return False ## Device not found
    else:
        err = 1
        return True


def RTP_connect():
    global err
    if not 'rtp' in get_sink()[2]: #only create sink once
        try:
            sink_properties = '''sink_properties="device.description='RTP stream2ip' device.bus='network' device.icon_name='network-server'"'''
            args = ['pactl', 'load-module','module-null-sink', 'sink_name=rtp', 'format=s16be', 'channels=2', 'rate=44100', sink_properties] #, 'format=s16be', 'channels=2',  'rate=44100',  '''description="RTP stream2ip"''']
            subprocess.Popen(args)
            args = ['pactl', 'load-module', 'module-rtp-send', 'source=rtp.monitor', 'loop=0']
            subprocess.Popen(args)
        except:
            debug_print(sys.exc_info())
            err = 2
            print('<E> RTP module for pulseaudio not found')
            return 0
    error = set_sink('rtp')
    if 'does not exist' in error: # that is in the PA Error-Msg
        err = 3
        return 0
    else:
        err = 0
        return 'RTP'


def Ice_connect(path): # path .m3u > Ices, local / live / .cfg > Darkice, .xml > Ices2
    global err, runpath, homepath, IceSystemwide, IceCredentials, IceServer
    IceServer = "icecast2" ## e.g. DEBIAN based distro
    if not shutil.which(IceServer):
        IceServer = "icecast" ## e.g. ARCH based distro
    elif not shutil.which(IceServer):
        messagebox(Gtk.MessageType.ERROR, 'Icecast was not found','Please install package <b>icecast2</b> or <b>icecast</b>')
        return 0
    if not IceSystemwide:
        if not os.path.isfile(homepath + 'icecast.xml'):
            shutil.copy(runpath + 'icecast.xml', homepath)
            with open(homepath + 'icecast.xml') as f: # update path for icecast.xml
                icecast_cfg = f.read()
                f.close()
            icecast_cfg = icecast_cfg.replace('/home/USER/.config/stream2ip/', homepath)
            with open(homepath + 'icecast.xml', mode = 'w') as f:
                f.write(icecast_cfg)
                f.close()
            debug_print('Created icecast.xml in ' + homepath)
    if path == 'local' or path == 'live':
        path = homepath + 'darkice-s2ip.cfg' # we stream local sound
    debug_print('Connecting to ' + path)
    IceCredentials = get_Icecredentials(path) ###################
    if not os.path.isfile(homepath + 'ices-s2ip.xml'): # copy defaults
        shutil.copy(runpath + 'ices-s2ip.xml', homepath)
        debug_print('New Ices2 (ogg) ices-s2ip.xml created in ' + homepath)
    if not os.path.isfile(homepath + 'ices-s2ip.conf'): # copy defaults
        shutil.copy(runpath + 'ices-s2ip.conf', homepath)
        debug_print('New Ices (mp3) ices-s2ip.config created in ' + homepath)
    if not os.path.isfile(homepath + 'darkice-s2ip.cfg'): # copy defaults
        shutil.copy(runpath + 'darkice-s2ip.cfg', homepath)
        debug_print('New Darkice (mp3) darkice-s2ip.cfg created in ' + homepath)
    if not os.path.isfile(path):
        err = 4
        debug_print('File not found:'+path)
        return 0
    if '.xml' in path: #stream with Ices2 from local ########################
        return stream_Ices2(path)
    if '.cfg' in path: #stream live mp3 with Darkice #########################
        return stream_Darkice(path)
    if '.m3u' in path: # stream mp3 playlist with Ices######################
        return stream_Ices(path)
    messagebox(Gtk.MessageType.ERROR, 'Bad configuration file','Unknown file type '+ path + '\nExtensions .xml, .cfg, or .m3u are valid only.')
    debug_print("<E> Bad configuration files for Icecast")
    err = 4
    return 0


def icecast_start():
## run in userspace this needs an icecast2.xml there
    global IceServer
    if getpid(IceServer): # already running maybe sytemwide (?)
        return 1
    elif IceServer == "icecast2":
        if not os.path.isdir(homepath + IceServer):
            os.mkdir(homepath + IceServer)
        args = [IceServer, "-c", homepath + 'icecast2.xml']
        try:
            debug_print("Starting Icecast2")
            subprocess.Popen(args)
        except:
            debug_print(sys.exc_info())
            messagebox(Gtk.MessageType.ERROR, 'Icecast2 could not be started')
            debug_print('<E> Icecast2 could not run ==> check icecast.xml for errors')
            return 0
    elif IceServer == "icecast":
        if not os.path.isdir(homepath + IceServer):
            os.mkdir(homepath + IceServer)
        args = [IceServer, "-c", homepath + 'icecast.xml']
        try:
            debug_print("Starting Icecast")
            subprocess.Popen(args)
        except:
            debug_print(sys.exc_info())
            messagebox(Gtk.MessageType.ERROR, 'Icecast could not be started')
            debug_print('<E> Icecast could not run ==> check icecast.xml for errors')
            return 0    
    return 1


def stream_Ices2(path): # streams in ogg
    global err

    if not icecast_start():
        err = 3
        return 0
    try:
        args = ["ices2", path] #start Ices2 for streaming from soundcard
        
    except:
        debug_print(sys.exc_info())
        err = 2
        messagebox(Gtk.MessageType.ERROR, 'Ices2 was not found','Please install ices2')
        debug_print('<E> Icecast/Ices2 not found! ==> Install <icecast, ices2> ')
        return 0
    pid = getpid("ices2")
    if pid:
        debug_print("Ices2 using " + path + " runs with PID: " + str(pid))
        err = 0
        return pid
    else:
        err = 3
        return 0


def stream_Darkice(path): # streams in mp3
    global err
    if not icecast_start():
        err = 3
        return 0
    try:
        args = ["darkice", "-c", path]
        subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    except:
        debug_print(sys.exc_info())
        err = 2
        messagebox(Gtk.MessageType.ERROR, 'Darkice was not found','Please install darkice')
        debug_print('<E> Icecast/Darkice not found! ==> Install <icecast, darkice> to fix.')
        return 0 # no good idea to call darkice
    pid = getpid("darkice")
    if pid:
        debug_print("Darkice using " + path + " runs with PID: " + str(pid))
        err = 0
        return str(pid)
    else:
        err = 3
        return 0


def stream_Ices(path): #streams mp3 from a playlist
    global err
    if not icecast_start():
        err = 3
        return 0
    try:
        args = ["ices", "-c", homepath + "ices-s2ip.conf", "-F", path]
        subprocess.Popen(args)
    except:
        debug_print(sys.exc_info())
        err = 2
        messagebox(Gtk.MessageType.ERROR, 'Ices was not found','Please install ices')
        debug_print('<E> Icecast/Ices not found! ==> Install <Icecast, ices> to fix.')
        return 0 # no good idea to call ices or ices2
    pid = getpid("ices")
    if pid:
        debug_print("Ices streaming: " + path + " with PID: " + str(pid))
        status.set_label('<b>Playlist: ' + path.rsplit('/',1)[1] + '</b>')
        err = 0
        return str(pid)
    else:
        err = 3
        return 0


def Ice_disconnect(pid):
    global IceServer
    debug_print('Disconnecting Icecast/Ices')
    args = ["kill", str(pid)] # terminate Ices/Ices2/Darkice
    subprocess.Popen(args)
    if not IceSystemwide: # terminate Icecast in userspace
        debug_print("Stopping Icecast in userspace")
        args = ["killall", IceServer]
        subprocess.Popen(args)
    return 0


def run_command(args):
    try:
        pid = subprocess.Popen(args, shell = True, stderr = subprocess.DEVNULL, stdout = subprocess.DEVNULL).pid
        debug_print('Subprocess ' + args[0] + ' called ' + str(pid))
    except:
        debug_print(sys.exc_info())
        pid = 0
        print('<E> Bad command: ' + args)
    return pid


def disconnect(device): # Module and sink are unloaded
    global pamodul, err, timeout, ConnectLoop, isloop, connected, icepid, defaults
    if device == 'DLNA live':
        restore_padefault()
        debug_print('Terminating DLNA server pulseaudio-dlna')
        time.sleep(3) ## time needed for stream recovery
        countdown = 10
        while getpid('pulseaudio-dlna') and countdown:
            debug_print('Waiting for process to terminate ' + str(timeout))
            subprocess.call(['killall', 'pulseaudio-dlna']) ## wait until pulseaudio-dlna terminated
            time.sleep(1)
            countdown -= 1
        if not countdown:
            print('<E> Failed to kill pulseaudio-dlna')
            exit(1)
        debug_print('<done>')
        pamodul = 0
    elif device == 'UPnP-Device':
        args = ["kill", str(pamodul)] # pamodul is PID
        subprocess.Popen(args)
        debug_print('UpnP server terminated: ' + str(pamodul))
        pamodul = 0
    elif device == 'Internet Radio':
        pamodul = Ice_disconnect(icepid)
    elif device == 'RTP/Multicast':
        restore_padefault()
        pamodul = 0
    elif device == 'None':
        pamodul = 0
    elif device == 'Avahi':
        pamodul = 0
        restore_padefault()
    else:
        return True
    status.set_label(State_Disconnected)
    err = 0
    Icon_layout('grey')
    return False


def restore_padefault():
    global default_sink
    set_sink(default_sink)
    debug_print('PulseAudio default sink restored')
    return


def ResetServer(): # this kills PulseAudio server
    global err, pamodul
    disconnect(pamodul)
    try:
        debug_print('Going to kill PulseAudio')
        subprocess.Popen("pulseaudio -k", shell=True) # raw but efficient
    except:
        debug_print('<E> failed to kill PulseAudio')
    Icon_layout('grey')
    status.set_label(State_Reset)
    err = 0
    return False


def device_ready(modul): # change layout and minimize
    global defaults, devices, err, Current_Icon
    pos = int(defaults[0])
    PA_Device = devices[pos]
    modstring = str(modul)
    osout.hide()
    if pos == 4 or pos == 6:
        entrybox.hide()
    else:
        entrybox.show()
    fcbutton.hide()
    ffwdbutton.show()
    if ConnectLoop:
        modstring = '<i> Auto</i>'
    if modul == 0:
        if err:
            Icon_layout('attention')
            Current_Icon = Icon_Attention
            if err == 2:
                status.set_label(Err_Msg[err])
                messagebox(Gtk.MessageType.ERROR, Err_Msg[err],'Run preferences to view packages needed')
            if err == 3:
                status.set_label(Err_Msg[err])
                messagebox(Gtk.MessageType.ERROR, 'A subprocess returned with an error.','''Run "stream2ip -v" in a terminal for details''')
            else:
                status.set_label(PA_Device + State_Notfound + Err_Msg[err])
        else:
            Icon_layout('grey')
            Current_Icon = Icon
            status.set_label(Err_Msg[err])
        return False
    elif PA_Device == 'UPnP-Device':
        Icon_layout('red')
        Current_Icon = Icon_red
        fcbutton.show()
        ffwdbutton.hide()
        status.set_label(PA_Device + State_Connected + modstring)
    elif PA_Device == 'DLNA live':
        Icon_layout('green')
        Current_Icon = Icon_green
        fcbutton.hide()
        ffwdbutton.show()
        status.set_label(PA_Device + State_Connected + modstring)
    elif PA_Device == 'RTP/Multicast':
        Icon_layout('red')
        Current_Icon = Icon_red
        entrybox.hide()
        status.set_label(PA_Device + State_Connected + modstring)
    elif PA_Device == 'Internet Radio':
        Icon_layout('red')
        Current_Icon = Icon_red
        fcbutton.show()
        status.set_label(PA_Device + State_Connected + modstring)
    elif modul == 'None':
        Icon_layout('black')
        Current_Icon = Icon_black
        entrybox.hide()
        ffwdbutton.hide()
    else:
        Icon_layout('green')
        Current_Icon = Icon_green
        status.set_label(PA_Device + State_Connected + modstring)
    if defaults[9] == 'Y': # do we minimize?
        window.hide()
    return True


def status_clicked(s_icon): # Maximize window when status icon clicked
    window.present()
    window.grab_focus()
    return


def Icon_layout(colour): # Layout settings dep on state
    global ConnectLoop
    if colour == 'grey': # no connection
        image.set_from_file(Icon)
        window.set_icon(AppIcn)
        cbutton.set_label(Connect)
    elif colour == 'orange': # on Check Loop when device not ready!
        image.set_from_file(Icon_orange)
        window.set_icon(OFFIcn)
        if ConnectLoop:
            cbutton.set_label(Stop)
        else:
            cbutton.set_label(Connect)
    elif colour == 'blue': # Bluetooth
        image.set_from_file(Icon_blue)
        window.set_icon(BlueIcn)
        cbutton.set_label(Disconnect)
    elif colour == 'green': # AirPort Express
        image.set_from_file(Icon_green)
        window.set_icon(ONIcn)
        cbutton.set_label(Disconnect)
    elif colour == 'black': # OS Command
        image.set_from_file(Icon_black)
        window.set_icon(BlackIcn)
        cbutton.set_label(Disconnect)
    elif colour == 'attention':
        image.set_from_file(Icon_Attention)
        window.set_icon(AttIcn)
        cbutton.set_label(Connect)
    elif colour == 'red': # red ON-AIR for INet Radio UPnP other
        image.set_from_file(Icon_red)
        window.set_icon(RedIcn)
        cbutton.set_label(Disconnect)
    if use_appind:
        if colour == 'grey': # no connection
            ind.set_status(appindicator.IndicatorStatus.ACTIVE)
        elif colour == 'orange': # on Check Loop when device not ready!
            ind.set_attention_icon(pIcon_o)
            ind.set_status(appindicator.IndicatorStatus.ATTENTION)
        elif colour == 'blue': # Bluetooth
            ind.set_attention_icon(pIcon_b)
            ind.set_status(appindicator.IndicatorStatus.ATTENTION)
        elif colour == 'green': # AirPort Express
            ind.set_attention_icon(pIcon_g)
            ind.set_status(appindicator.IndicatorStatus.ATTENTION)
        elif colour == 'black': # OS Command
            ind.set_attention_icon(pIcon_k)
            ind.set_status(appindicator.IndicatorStatus.ATTENTION)
        elif colour == 'attention':
            ind.set_attention_icon(pIcon_Att)
            ind.set_status(appindicator.IndicatorStatus.ATTENTION)
        elif colour == 'red': # red ON-AIR for INet Radio UPnP other
            ind.set_attention_icon(pIcon_r)
            ind.set_status(appindicator.IndicatorStatus.ATTENTION)
    return


def ice_nowplaying():
    path = ''
    try:
        with open('/tmp/ices.log', 'r+') as f: # load last IP from file
                message = f.read()
    except:
        debug_print(sys.exc_info())
        debug_print('ices.log not found')
        return ''
    if 'Playing' in message:
        path = message.rsplit('Playing ', 1)[1]
        path = path.split('\n')[0]
    f.close()
    if os.path.isfile(path):
        return path
    else:
        return ''


def get_tags_from_file(path):
    metadata = {"artist": '-', "title": '-', "location": 'empty', "arturl": 'none'}
    path1 = path.rsplit('/', 1)
    mime = path.rsplit('.', 1)[1]
    metadata["arturl"] = 'file://'+ path1[0] + '/cover.jpg'
    metadata["location"] = path1[0] + '/'
    metadata["title"] = path1[1]
    if (pymutagen and mime == 'mp3'): # we can only do this with mp3 files
        id3 = MP3(path, ID3=EasyID3)
        metadata["artist"] = id3["artist"][0]
        metadata["title"] = id3["title"][0]
    return metadata


def control_player(mplayer, action): # controls playback of MPRIS2 player
    global mpris_v
    if getpid(mplayer['prgname']): # is the player still running?
        try:
            bus = dbus.SessionBus()
            device = bus.get_object(mplayer['mprisname'], mplayer['mprispath'])
            if mpris_v == 2:
                propiface = dbus.Interface(device, dbus_interface = 'org.mpris.MediaPlayer2.Player')
            elif mpris_v == 1:
                propiface = dbus.Interface(device, dbus_interface = 'org.freedesktop.MediaPlayer')
            if action == 'stop':
                propiface.Stop()
            elif action == 'play':
                propiface.Play()
            elif action == 'pause':
                propiface.Pause()
            elif action == 'next':
                propiface.Next()
            elif action == 'prev':
                propiface.Previous()
        except:
            debug_print(sys.exc_info())
            debug_print('DBUS error on player control: ' + action)
    else:
        debug_print('Player not running')
    return


def get_metadata(mplayer): # for MPRIS 1.0
    global coverart, mpris_v
    mpris_v = 1
    coverart = mplayer['artfile']
    metadata = {"artist": '-', "title": '-', "location": 'empty', "arturl": 'none'}
    try:
        bus = dbus.SessionBus()
        device = bus.get_object(mplayer['mprisname'], mplayer['mprispath'])
        iface = dbus.Interface(device, dbus_interface='org.freedesktop.MediaPlayer')
        meta1data = iface.GetMetadata()
        metadata["artist"] = meta1data['artist']
        metadata["title"] = meta1data['title']
        metadata["location"] = meta1data['location']
        try:
            metadata["arturl"] = meta1data['arturl']
        except:
            debug_print(sys.exc_info())
            metadata["arturl"] = meta1data['location'] # 'arturl' may not exist
    except:
        debug_print(sys.exc_info())
        return ''
    return metadata


def get_metadata2(mplayer): #for MPRIS 2.0
    global playerstate, coverart, mpris_v
    mpris_v = 2
    coverart = mplayer['artfile']
    metadata = {"artist": '-', "title": '-', "location": 'empty', "arturl": 'none'} #for compatibility with MPRIS 1.0
    try:
        bus = dbus.SessionBus()
        device = bus.get_object(mplayer['mprisname'], mplayer['mprispath'])
        propiface = dbus.Interface(device, dbus.PROPERTIES_IFACE)
        playerstate = propiface.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')
        if playerstate == 'Playing':
            try: # don't assume there are any
                meta2data = propiface.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
                metadata["artist"] = meta2data['xesam:artist'][0]
                metadata["title"] = meta2data['xesam:title']
                metadata["location"] = meta2data['xesam:url']
                metadata["arturl"] = meta2data['mpris:artUrl']
            except:
                return metadata
    except:
        debug_print(sys.exc_info())
        return ''
    return metadata


def track_changed(metadata):
    global defaults
    if metadata:
        display_metatags(metadata)
        if defaults[0] == '5': # on 'Internet Radio' mode only
            send_metatags(metadata)
    return True


def display_metatags(metadata):
    global coverart, Current_Icon
    s = metadata["arturl"]
    if s == 'none':
        imagepath = Current_Icon
    elif os.path.isfile(s):
        imagepath = s
    elif '//' in s:
        imagepath = s.split('//', 1)[1] # strip "file://"
        if not os.path.isfile(imagepath):
            s = metadata["location"]
            imagepath = s.split('//', 1)[1] # strip "file://"
            imagepath = imagepath.rsplit('/', 1)[0] + '/' + coverart
            try:
                if sys.version >= '3':
                    imagepath = urllib.parse.unquote(imagepath)
                else:
                    imagepath = urllib.unquote(imagepath)
            except:
                debug_print('<E> Bad link to cover art')
        if not os.path.isfile(imagepath):
            imagepath = Current_Icon
    else:
        imagepath = Current_Icon
    artist = metadata["artist"]
    title = metadata["title"]
    try:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(imagepath)
    except:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(Current_Icon)
        debug_print('<E> Bad cover art definition')
    scaled_buf = pixbuf.scale_simple(96, 96, GdkPixbuf.InterpType.BILINEAR)
    image.set_from_pixbuf(scaled_buf)
    image.show()
    display = '<b>' + artist + " - " + title + '</b> '
    display = display.replace('&', '&amp;')
    status.set_label(display)
    return


def send_metatags(metadata):# send metadata to the Icecast server
    global defaults, homepath, IceCredentials
    return
########## this is broken ATM ##########################################
    configpath = defaults[6]
    tag = metadata["artist"] + ' - ' + metadata["title"]
    specialchars = '#$§&%@'
    if sys.version >= '3':  ## remove non-ASCII for Python3 only
        tag = ''.join(c for c in tag if c not in specialchars) ## remove special chars
        tag = tag.encode(encoding = "ascii", errors = "replace")
        tag = tag.decode()
    tag = tag.replace(' ', '+') #blanks need to be '+' for Icecast2
    if (configpath == 'local' or configpath == 'live'):
        configpath = homepath + 'darkice-s2ip.cfg'
#    if not IceCredentials[2]:
    IceCredentials = get_Icecredentials(configpath)
    iceurl = 'http://' + IceCredentials[2] + ':' + IceCredentials[3] + "/admin/metadata?mount=/" + IceCredentials[4] + "&mode=updinfo&song=" + tag
    try:
        if sys.version >= '3': ## we are on Python3
            passmanager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            passmanager.add_password(None, iceurl, IceCredentials[0], IceCredentials[1])
            authhandler = urllib.request.HTTPBasicAuthHandler(passmanager)
            urlopener = urllib.request.build_opener(authhandler)
            urllib.request.install_opener(urlopener)
            urllib.request.urlopen(iceurl)
        else: ## we are on Python2
            passmanager = urllib2.HTTPPasswordMgrWithDefaultRealm()
            passmanager.add_password(None, iceurl, IceCredentials[0], IceCredentials[1])
            authhandler = urllib2.HTTPBasicAuthHandler(passmanager)
            urlopener = urllib2.build_opener(authhandler)
            urllib2.install_opener(urlopener)
            urllib2.urlopen(iceurl)
        debug_print('Metatags updated to: ' + tag) 
    except:
        debug_print(sys.exc_info())
        debug_print('Bad URL: updating metatags failed')
    return


def get_Icecredentials(path):
    global defaults, ice_mount, PA_Device, homepath, IceServer
    if '.m3u' in path:
        path = homepath + 'ices-s2ip.conf'
    credentials = ['admin', 'pass', 'IP', 'port', 'mount']
    if os.path.isfile(path):
        with open(path) as f: # load Ices/Darkice settings from file
            ices_cfg = f.read()
        f.close()
    else:
        messagebox(Gtk.MessageType.ERROR, 'File not found','Configuration '+ path + ' does not exist')
        debug_print("<E> Configuration not found: " + path)
        return ''
    icecfg = ices_cfg.replace(' ', '') #remove blanks
    if '.cfg' in path: # Darkice
        credentials[4] = string_mstrip(icecfg, 'mountPoint=', '#')
        credentials[2] = string_mstrip(icecfg, 'server=', '#')
        credentials[3] = string_mstrip(icecfg, 'port=', '#')
    elif '.conf' in path: # Ices Playlist
        credentials[4] = string_mstrip(icecfg, '<Mountpoint>/', '</Mountpoint>')
        credentials[2] = string_mstrip(icecfg, '<Hostname>', '</Hostname>')
        credentials[3] = string_mstrip(icecfg, '<Port>', '</Port>')
    elif '.xml' in path: # Ices2
        credentials[4] = string_mstrip(icecfg, '<mount>/', '</mount')
        credentials[2] = string_mstrip(icecfg, '<hostname>', '</hostname>')
        credentials[3] = string_mstrip(icecfg, '<port>', '</port>')
    ice_mount = credentials[4]
    if credentials[2] == 'localhost':

        retcode = subprocess.Popen(['hostname', '-I'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        localip = retcode.communicate()[0].decode()
        if localip:  ## DEBIAN
            credentials[2] = localip.strip('\n')
        else: ## other
            retcode = subprocess.Popen(["ip","route","get","1"], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            localip = retcode.communicate()[0].decode()
        if localip:
                 print("DEBUG: " + localip)
                 credentials[2] = localip.rsplit("src ",1)[1].rsplit(" uid",1)[0]
        else:
            debug_print("<W> IP of localhost could not be determined")
    debug_print('Mount Point is ' + credentials[2] + ":" + credentials[3] +"/" + credentials[4])
    dlabel.set_label('<b>' + credentials[2] + ':' + credentials[3] + '/' + credentials[4] + '</b>')
    if IceSystemwide:
        path = '/etc/' + IceServer + '/icecast.xml'
    else:
        path = homepath + 'icecast.xml'
    try:
        with open(path) as f:
            icxml = f.read()
        f.close()
    except:
        debug_print(sys.exc_info())
        if defaults[16] == 'hackme':
            messagebox(Gtk.MessageType.ERROR, 'Icecast configuration not accessible','Configuration '+ path + ' can not be read.\n Please change permissions to allow read access.\Continu with default values now.')
        debug_print("<E> Can't read configuration file for Icecast")
        credentials[0] = defaults[15]
        credentials[1] = defaults[16]
        return credentials
    credentials[0] = string_mstrip(icxml, '<admin-user>', '</admin-user>')
    credentials[1] = string_mstrip(icxml, '<admin-password>', '</admin-password>')
    defaults[15] = credentials[0]
    defaults[16] = credentials[1]
    return credentials


def string_mstrip(s, lchars, rchars): # strips left from lchars and right from rchars
    return s.split(lchars, 1)[1].split(rchars, 1)[0]


def set_sink(i): # sets pulseaudio sink i (index or name) as default
    global mplayers, defaults, ConnectLoop, err
    try:
        cl = ConnectLoop
        ConnectLoop = False #wait with looping until sink change done
        args = "pacmd set-default-sink " + i
        retcode = subprocess.Popen(args, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        status = retcode.communicate()[1].decode()
        debug_print('Default sink set to ' + i + ' ' + status)
        input_index = get_streaminput_index()
        if input_index: #move sink playback to new sink
            args = "pacmd move-sink-input " + input_index + ' ' + i
            retcode = subprocess.Popen(args, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            status = retcode.communicate()[1].decode()
            debug_print('Stream index ' + input_index + ' was moved ' + status)
        ConnectLoop = cl # restore loop state
        return status # return errors
    except:
        debug_print(sys.exc_info())
        err = 2
        debug_print('<E> Failed to set sink in pulseaudio')
        return 'Error'


def save_quit(arg1, arg2):
    global defaults, connected, PA_Device, ConnectLoop
    ConnectLoop = False
    if defaults[7] == 'Y':
        s2ip_setup.save_defaults(defaults, homepath)
    if connected:
        if defaults[10] == 'Y': # disconnect on quit
            debug_print('Going to disconnect: ' + PA_Device)
            connected = disconnect(PA_Device)
    Gtk.main_quit()
    debug_print('Bye Bye')
    exit() # bye bye


def debug_print(arguments):
    timestmp = time.strftime("%Y-%m-%d:%H:%M:%S>> ", time.localtime())
    if verbous:
        print(' [STREAM2IP] ' + timestmp, arguments)
    if logfile:
        with open(homepath + 'stream2ip.log', 'a') as f: # append to logfile
            f.write(timestmp)
            f.write(str(arguments))
            f.write("\n")
        f.close()
    return
#
################################################################################
# The GUI: #####################################################################
################################################################################
xml = Gtk.Builder()
xml.add_from_file(runpath + 'glade/stream2ip.ui')

## Main window #################################################################
window = xml.get_object('dialog1')
window.connect("delete_event", save_quit) #connect to save quit!
cbutton = xml.get_object('connectbutton')
qbutton = xml.get_object('quitbutton')
rbutton = xml.get_object('resetbutton')
sbutton = xml.get_object('setupbutton')
hbutton = xml.get_object('helpbutton')
fcbutton = xml.get_object('fchoose_button')
ffwdbutton = xml.get_object('ffwd_button')
#bckbutton = xml.get_object('back_button')
dlabel = xml.get_object('dev_label')
introtxt = xml.get_object('introtxt')
cbutton.set_label(Connect)
qbutton.set_label(Quit)
introtxt.set_label('<small>' + Intro_Text+ version + ' - ' + s2ip_setup.distribution[0] + ' ' + s2ip_setup.distribution[1] + '</small>')
image = xml.get_object('image1')
status = xml.get_object('label2')
osout = xml.get_object('textbox')
buttonid = cbutton.connect("button-release-event", on_button_clicked)
buttonid = qbutton.connect("button-release-event", on_button_clicked)
buttonid = rbutton.connect("button-release-event", on_button_clicked)
buttonid = sbutton.connect("button-release-event", on_button_clicked)
buttonid = hbutton.connect("button-release-event", on_button_clicked)
buttonid = fcbutton.connect("button-release-event", on_button_clicked)
buttonid = ffwdbutton.connect("button-release-event", on_button_clicked)
#buttonid = bckbutton.connect("button-release-event", on_button_clicked)
entrybox = xml.get_object('entry1')
AppIcn = GdkPixbuf.Pixbuf.new_from_file(Icon)
ONIcn = GdkPixbuf.Pixbuf.new_from_file(Icon_green)
OFFIcn = GdkPixbuf.Pixbuf.new_from_file(Icon_orange)
BlueIcn = GdkPixbuf.Pixbuf.new_from_file(Icon_blue)
RedIcn = GdkPixbuf.Pixbuf.new_from_file(Icon_red)
BlackIcn = GdkPixbuf.Pixbuf.new_from_file(Icon_black)
AttIcn = GdkPixbuf.Pixbuf.new_from_file(Icon_Attention)
window.set_default_icon(AppIcn)
# window.set_default_icon_from_file(Icon)

## Help window #################################################################
help_window = xml.get_object('help')
help_quit = xml.get_object('help_quit')
help_online = xml.get_object('help_online')
buttonid = help_quit.connect("button-release-event", on_button_clicked)
buttonid = help_online.connect("button-release-event", on_button_clicked)
help_intro = xml.get_object('help_intro_text')
help_general = xml.get_object('help_general_text')
help_airport = xml.get_object('help_airport_text')
help_bluetooth = xml.get_object('help_bluetooth_text')
help_upnp = xml.get_object('help_upnp_text')
help_dlnalive = xml.get_object('help_dlnalive_text')
help_inetradio = xml.get_object('help_inetradio_text')
#
help_intro.set_label(version + '\n\n' + help_intro_txt)
help_general.set_label(help_general_txt)
help_airport.set_label(help_airport_txt)
help_bluetooth.set_label(help_bluetooth_txt)
help_upnp.set_label(help_upnp_txt)
help_dlnalive.set_label(help_dlnalive_txt)
help_inetradio.set_label(help_inetradio_txt)
###

# define d-bus loop
gloop = '' #GObject.MainLoop() # define loop as global
bus_loop = '' #DBusGMainLoop(set_as_default=True)
bus = '' #dbus.SessionBus(mainloop=bus_loop)


# define Application Indicator
def quit_from_AppI(arg1, arg2):
    save_quit(None, None)


def show_from_AppI(arg1, arg2):
    window.present()


def connect_from_AppI(arg1, arg2):
    global defaults, connected, ConnectLoop, PA_Device, timeout, pamodul, runcommand
    pos = int(defaults[0])
    PA_Device = devices[pos]
    status.set_label(State_Wait)
    defaults[pos+1] = entrybox.get_text() # in case edited
    if not connected:
        status.set_label(State_Searching + PA_Device)
        debug_print('Going to connect with ' + PA_Device)
        connected = connect(defaults)
        if not connected:
            debug_print('<E> Connection failed. Device: '+ PA_Device)
        elif defaults[12] and runcommand:
            runcommand = False
            run_command(defaults[12]) # run command after setup
        device_ready(pamodul)
        if timeout:
            ConnectLoop = True
    return


def disconnect_from_AppI(arg1, arg2):
    global PA_Device, connected, ConnectLoop
    if connected:
        debug_print('Going to disconnect: ' +PA_Device)
        ConnectLoop = False
        connected = disconnect(PA_Device)
    return


################################################################################
### Appplication Indicator #####################################################
################################################################################

if use_appind:
    try:
        gi.require_version('AppIndicator3', '0.1')
        from gi.repository import AppIndicator3 as appindicator
        use_appind = True
        ind = appindicator.Indicator.new("stream2ip", pIcon, appindicator.IndicatorCategory.APPLICATION_STATUS)
        ind.set_status(appindicator.IndicatorStatus.ACTIVE)
        ind.set_attention_icon(pIcon_Att)
        AppImenu = Gtk.Menu()
            # Status Menus
        showmenu = Show
        AppImenu_item_show = Gtk.MenuItem(showmenu)
        AppImenu.append(AppImenu_item_show)
        connectmenu = Connect
        AppImenu_item_connect = Gtk.MenuItem(connectmenu)
        AppImenu.append(AppImenu_item_connect)
        disconnectmenu = Disconnect
        AppImenu_item_disconnect = Gtk.MenuItem(disconnectmenu)
        AppImenu.append(AppImenu_item_disconnect)
        quitmenu = Quit
        AppImenu_item_quit = Gtk.MenuItem(quitmenu)
        AppImenu.append(AppImenu_item_quit)
            # Menu Actions
        buf =''
        AppImenu_item_quit.connect("activate", quit_from_AppI, buf)
        AppImenu_item_show.connect("activate", show_from_AppI, buf)
        AppImenu_item_connect.connect("activate", connect_from_AppI, buf)
        AppImenu_item_disconnect.connect("activate", disconnect_from_AppI, buf)
            # display menus
        AppImenu_item_show.show()
        AppImenu_item_quit.show()
        AppImenu_item_connect.show()
        AppImenu_item_disconnect.show()
        ind.set_menu(AppImenu)
    except:
        ind = ''
        use_appind = False


def messagebox(mess_type, title, message):
    self = Gtk.Window()
    dialog = Gtk.MessageDialog(self, 0, mess_type, Gtk.ButtonsType.OK, title)
    dialog.format_secondary_markup(message)
    dialog.run()
    dialog.destroy()


def get_pamodules():
    try:
        retcode = subprocess.Popen(['pactl', 'list', 'short', 'modules'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        status = retcode.communicate()
        return(status[0].decode()) # all modules loaded
    except:
        debug_print(sys.exc_info())
        debug_print('<E> unable to run pulseaudio command to get module list')
        return ''


def get_sink(): # returns the present default sink index as string
    sinks = ['', '', '', '']
    try: # only if we run pulseaudio
        retcode = subprocess.Popen(['pacmd', 'list-sinks'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        status = retcode.communicate()
        allsinks = status[0].decode() # all sinks
        lastsink_index = allsinks.rsplit('index: ', 1)[1].split('\n')[0]
    except:
        debug_print(sys.exc_info())
        debug_print('<E> unable to run pulseaudio command to get sinks')
        return ['', '', '', '']
    if '*' in allsinks:
        index = allsinks.split('* index: ', 1)[1].split('name:', 1)[0]
        name = allsinks.split('* index: ' + index + 'name: <', 1)[1].split('driver:', 1)[0]
        name = name.replace('>\n\t', '')
        index = index.replace('\n\t', '')
#    debug_print('Index: ' + index + ' Name: ' + name)
        sinks[0] = index # default sink index
        sinks[1] = name # default sink name
    sinks[2] = allsinks # all sinks and parameters
    sinks[3] = lastsink_index # last sink index in use
    return sinks


def get_streaminput_index(): # returns the present stream input index
    index = ''
    retcode = subprocess.Popen("pacmd list-sink-inputs", shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    status = retcode.communicate()
    allinputs = status[0].decode() # all inputs
    if 'index' in allinputs:
        index = allinputs.rsplit('state: RUNNING', 1)[0].rsplit('index: ', 1)[1].rsplit('driver:', 1)[0]
        index = index.replace('\n\t', '')
    debug_print('Input Index: ' + index)
    return index


def main():
    global pamodul, defaults, timeout, ConnectLoop, CheckLoop, devices, connected, homepath, PA_Device, default_sink, runcommand, IceSystemwide, IceServer
    debug_print('*** Starting stream2ip ' + version + ' ' + str(s2ip_setup.distribution) + ' ***')
    IceSystemwide = getpid(IceServer) # whether iceast already runs
    if IceSystemwide:
        debug_print("Icecast already running: " + str(IceSystemwide))
    default_sink = get_sink()[0]
    debug_print("Default audio sink: " + default_sink)
    if defaults[15] == '?': #for compatibility with s2ip 2.x
        defaults[15] = 'admin'
        defaults[16] = 'hackme'
    timeout = defaults[13]
    if timeout:
        ConnectLoop = True
    debug_print('We are using these settings: ')
    debug_print(defaults)
    pos = int(defaults[0])
    PA_Device = devices[pos]
    AutoState = ''
    if defaults[13] and PA_Device == 'Bluetooth':
        AutoState = 'Autoconnect'
    dlabel.set_label('<b>' + PA_Device + AutoState + ':</b>')
    window.show_all()
    if pos == 6 or pos == 4:
        entrybox.hide()
    else:
        entrybox.set_text(defaults[pos+1])
    Icon_layout('grey')
    if pos == 3:
        fcbutton.hide()
    if defaults[8] == 'Y': # Autoconnect
        connected = connect(defaults)
        device_ready(pamodul)
    else:
        status.set_label(Err_Msg[0])
        Icon_layout('grey')
    Gtk.main()
    return


if __name__ == "__main__":
    main()
