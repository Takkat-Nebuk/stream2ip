#!/usr/bin/python3
#-*- coding: utf-8 -*-
#
###########################
# stream2ip - Setup       #
# Author: Takkat Nebuk    #
# Date: 2020-04-03        #
# Version: 1.1.6          #
###########################
# Python3 depends: python3-gi, python3-apt
#
import os
import shutil
import time
from gi.repository import Gtk, GdkPixbuf
from sys import argv
from sys import version as pyversion
import socket as s
try:
    import urllib.request
except:
    print('<W> Discovery of DLNA-renderers not supported with Python2')
use_apt = True
try:
    import apt
except:
    print('<W> Use your distribution package manager for installing recommends')
    use_apt = False
import subprocess
import distro
admin_mode = False
if '-admin' in argv: ##  disabling preferences can only be done from `s2ip_setup -admin'
    admin_mode = True
#
#
# set program paths
runpath = os.path.dirname(os.path.realpath(__file__)) + '/'
userhome = os.path.expanduser('~')
homepath = userhome + '/.config/stream2ip/'
distribution = distro.linux_distribution(full_distribution_name=False)  ### too long?
############################################################################
# Here's some init stuff:
lang = os.getenv("LANG")
spoken = lang.split("_") # returns [language, coding]
#if spoken[0] == 'de': # speak German?
#    from stream2ip_de import *
#else: # if not then maybe English
from stream2ip_en import *

setup_runsolo = True
setupIcon = runpath + 'icons/S2-setup.svg'

render_ip = []
render_name = []
render_url = []
default_renderer = ''
default_renderip = ''

#check installed packages
# 0 = Pulseaudio
# 1 = PA-utils
# 2 = RAOP
# 3 = ushare
# 4 = icecast2
# 5 = ices2
# 6 = bluetooth PA
# 7 = Bluez
# 8 = ices
# 9 = darkice
Package_needed = [
'''pulseaudio
''', '''pulseaudio-module-raop
''', '''ushare, minidlna or pulseaudio-dlna
''', '''icecast2
''', '''darkice, ices or ices2
''', '''pulseaudio-module-bluetooth
''', '''bluez
''']

#Media Players supported:
mplayers = [
{'name':'None', 'prgname':'', 'mprisname':'', 'mprispath':'', 'artfile':''},
{'name':'Amarok', 'prgname':'amarok', 'mprisname':'org.mpris.MediaPlayer2.amarok', 'mprispath':'/org/mpris/MediaPlayer2', 'artfile':'cover.jpg'},#+
{'name':'Audacious', 'prgname':'audacious', 'mprisname':'org.mpris.MediaPlayer2.audacious', 'mprispath':'/org/mpris/MediaPlayer2', 'artfile':'cover.jpg'},#+
{'name':'Banshee', 'prgname':'banshee', 'mprisname':'org.mpris.MediaPlayer2.banshee', 'mprispath':'/org/mpris/MediaPlayer2', 'artfile':'cover.jpg'},#+
{'name':'Clementine', 'prgname':'clementine', 'mprisname':'org.mpris.MediaPlayer2.clementine', 'mprispath':'/org/mpris/MediaPlayer2', 'artfile':'cover.jpg'},#+
#{'name':'GMusicbrowser', 'prgname':'gmusicbrowser', 'mprisname':'org.mpris.gmusicbrowser', 'mprispath':'/Player', 'artfile':'cover.jpg'}, #- non-standard MPRIS2 implementation
{'name':'Guayadeque', 'prgname':'guayadeque', 'mprisname':'org.mpris.MediaPlayer2.guayadeque', 'mprispath':'/org/mpris/MediaPlayer2', 'artfile':'cover.jpg'},#+
{'name':'Rhythmbox', 'prgname':'rhythmbox', 'mprisname':'org.mpris.MediaPlayer2.rhythmbox', 'mprispath':'/org/mpris/MediaPlayer2', 'artfile':'cover.jpg'}#+
]

#Streaming methods supported:
s2ip_methods = [
#{'name':'- deprecated -', 'position':'0', 'parameters':'', 'dependencies':''},
#{'name':'- deprecated -', 'position':'1', 'parameters':'', 'dependencies':''},
{'name':'UPnP/DLNA', 'position':'2', 'parameters':'media path', 'dependencies':''},
{'name':'DLNA live', 'position':'7', 'parameters':'', 'dependencies':''},
{'name':'RTP/Multicast', 'position':'3', 'parameters':'', 'dependencies':''},
{'name':'Internet Radio', 'position':'4', 'parameters':'live', 'dependencies':''},
{'name':'None', 'position':'5', 'parameters':'Preferences to set up streaming', 'dependencies':''},
]

packagelist = [
{'name':'pulseaudio', 'state':'yes'}, # 0
{'name':'pulseaudio-module-raop', 'state':'yes'}, # 1
{'name':'ushare', 'state':'yes'},# 2
{'name':'minidlna', 'state':'yes'}, # 3
{'name':'icecast2', 'state':'yes'}, # 4
{'name':'darkice', 'state':'yes'}, # 5
{'name':'ices2', 'state':'yes'}, # 6
{'name':'ices', 'state':'yes'}, # 7
{'name':'pulseaudio-module-bluetooth', 'state':'yes'}, # 8
{'name':'bluez', 'state':'yes'}, # 9
{'name':'pulseaudio-dlna', 'state':'yes'} # 10
]

state = [0,0,0,0,0, 0,0,0,0,0, 0] # 1 if needs to be installed

if use_apt:
    aptcache = apt.Cache()


def package_state(): ## apt independent
    for i in range(len(packagelist)):
        try:
            if shutil.which(packagelist[i]['name']):
                packagelist[i]['state'] = 'yes'
            else:
                packagelist[i]['state'] = 'no'
        except:
            packagelist[i]['state'] = 'no' # is not installed
        print(packagelist[i]['name'] + ' is installed: ' + packagelist[i]['state'])
        instpic[i].set_from_stock('gtk-' + packagelist[i]['state'],Gtk.IconSize.BUTTON)
    status_box.set_label('')
    return # [0 or False] if package is installed


def load_defaults(path):
    settings = ['6',
    '',
    '',
    '/path/music',
    '',
    'live',
    'Preferences to set up streaming',
    'N', 'N', 'N', 'Y', 'N',
    '', '4', '0', 'admin', 'hackme', 'N', 'N'] # in case all .cfg are lost
    if os.path.isfile(path + 's2ip.cfg'):
        with open(path + 's2ip.cfg', 'r') as f: # load settings from file
            text = f.read()
            oldsettings = text.split(",")
        f.close()
        if oldsettings[0] == '0' or oldsettings[0] == '1':
            messagebox(Gtk.MessageType.ERROR, "Please note that streams to  Airport Express\nor Bluetooth are no longer provided.", "")
            oldsettings[0] = '6'
        if not oldsettings[0]:  #someting bad happened to our cfg
            messagebox(Gtk.MessageType.ERROR, "Failed to read configuration","Going to use previous settings.")
            if os.path.isfile(path + 's2ip.cf~'):
                with open(path + 's2ip.cf~', 'r') as f: # backup file
                    text = f.read()
                    oldsettings = text.split(",")
                f.close()
            if not oldsettings[0]:
                return settings
        for i in range(len(oldsettings)):
            settings[i] = oldsettings[i]
        return settings
    elif not os.path.isdir(path):
        os.mkdir(path) # create ~/.stream2ip/
    return settings


def save_defaults(settings, path):
    if os.path.isfile(path + 's2ip.cfg'):
        os.rename(path + 's2ip.cfg', path + 's2ip.cf~') # make a backup
    with open(path + 's2ip.cfg', 'w') as f: # save settings
            f.write(','.join(str(i) for i in settings))
    add_startup(settings)
    f.close()
    return


def add_startup(settings):
    autodir = userhome + '/.config/autostart/'
    if settings[17] == 'Y': # add to startup apps
        if not os.path.isdir(autodir):
            os.mkdir(autodir)
        if not os.path.isfile(autodir + 'stream2ip-autostart.desktop'):
            shutil.copy(runpath + 'stream2ip-autostart.desktop', autodir + 'stream2ip-autostart.desktop')
    else:
        if os.path.isfile(autodir + 'stream2ip-autostart.desktop'):
            os.remove(autodir + 'stream2ip-autostart.desktop')
    return


def on_button_clicked(buttonid, event):
    global homepath
    global defaults
    position = device.get_active() + 2 ## 2 is needed because previous 0 and 1 are deprecated
    posplayer = player.get_active()
    if buttonid == sbutton:
        defaults[0] = str(position)
        defaults[14] = str(posplayer)
        defaults[position+1] = ip_entrybox.get_text()
        defaults = get_buttons(defaults)
        save_defaults(defaults, homepath)
        close(None, None)
    if buttonid == fchoose_button:
            chosenpath = ''
            if position == 2: # UPnP needs Folders
                chosenpath = f_choose('Folder')
            if position == 5:# Icecast may need a file
                chosenpath = f_choose('File')
            if position == 3: # DLNA live may need stream URL discovery
                f_choose('Setup')
                chosenpath = defaults[4]
            if chosenpath:
                ip_entrybox.set_text(chosenpath)
    elif buttonid == qbutton:
        close(None, None)
    return


def on_install_clicked(buttonid, event): ## apt dependent!
    global state, aptcache, use_apt
    installbox.hide()
    state = [0,0,0,0,0, 0,0,0,0,0, 0]
    packages = ''
    not_installables = ''
    selected = [0,0,0,0,0, 0,0,0,0,0, 0]
    for i in range(len(packagelist)):
        selected[i] = butt[i].get_active()
        if packagelist[i]['state'] == 'no' and selected[i]:
#            if packagelist[i]['name'] in aptcache: ## apt dependent
#            if shutil.which(packagelist[i]['name']): ## is the package cached?
            packages += packagelist[i]['name'] + ' '
            state[i] = 1
#            else:
#                not_installables += packagelist[i]['name'] + ' '
    print (selected) ## debug
    if not use_apt:
	    return
    if True in selected:
        args = "pkexec apt-get -y install " + packages
        print(args)
        if pyversion < '3':
            try:
                retcode = subprocess.Popen(args, shell = True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                s = retcode.communicate()[1]
                print(s)
            except:
                print('<E> Bad command: ' + args)
        else:
            try:
                with subprocess.Popen(args, shell = True, stderr=subprocess.PIPE, stdout=subprocess.PIPE) as proc:
                    s = proc.stdout.read().decode()
                print(s)
            except:
                print('<E> Bad command: ' + args)
        aptcache = apt.Cache()  ## refresh apt cache
        ptest = packages.split(' ')
        i_err = 0
        package_error = ''
        ## Test if installation was successful:
        for i in range(len(ptest) -1):  ## -1 because there is a blank
            print(i)
            try:
                if not aptcache[ptest[i]].is_installed:
                    i_err += 1
            except:
                i_err += 1
                print('<E> apt cache error for: ' + ptest[i])
            if i_err:
                package_error += ptest[i] + ' '
                print('<E> ' + ptest[i] + ' was not installed')
        if i_err or not_installables:
            messagebox(Gtk.MessageType.ERROR, "Package(s) could not be installed","Failed to install <b>" + package_error + not_installables + "</b>\n\nWe may need to add another software source or install manually.")
            state = [0,0,0,0,0, 0,0,0,0,0, 0]
        else:
            messagebox(Gtk.MessageType.INFO, "Successfully installed:", "<b>" + packages + "</b>\n\nSome applications need additional\nconfiguration before use with stream2ip.")
    return


def install_cancelled(buttonid, event):
    global state, defaults
    installbox.hide()
    state = [0,0,0,0,0, 0,0,0,0,0, 0]
    defaults[0] = '6'
    set_gui(defaults)
    return True


def on_combo_entry_changed(new_iter):
    global defaults
    global ip_label_txt
    position = device.get_active() +2 ## 0,1 are deprecated
    player.get_active()
    fchoose_button.hide()
    if position == 2 or position == 5 or position == 3:
        fchoose_button.show()
    if position == 4 or position == 6:
        ip_entrybox.hide()
        ip_label.set_text('')
        return
    if check_package(position):
        ip_entrybox.show()
        ip_entrybox.set_text(defaults[position + 1])
        ip_label.set_text(ip_label_txt[position])
        bta_button.set_value(int(defaults[13]))
    else:
        device.set_active(5)
        ip_entrybox.hide()
        ip_label.set_text(ip_label_txt[position])


def on_ipentry_changed(new_iter):
    global defaults
    position = device.get_active()
    defaults[position+1] = ip_entrybox.get_text()
    if position == 0 or position == 1 or position == 4 or position == 6: # not options
        defaults[5] = ''
        ip_entrybox.set_text('')


def on_cmdentry_changed(new_iter):
    global defaults
    defaults[12] = cmd_entrybox.get_text()


def close(arg1, arg2):
    global setup_runsolo, defaults
    if setup_runsolo:
        Gtk.main_quit()
        exit()
    else:
        setupwindow.hide()
        return defaults


def on_dlnaselect_clicked(new_iter, arg2):
    global render_ip, render_name, render_url, defaults
    pos = rendererbox.get_active()
    if render_ip[pos]:
        defaults[4] = render_name[pos] + '@' + render_ip[pos]
    else:
        defaults[4] = render_url[pos]
    ip_entrybox.set_text(defaults[4])
    dlnabox.hide()


def dlnaselect_cancelled(new_iter, arg2):
    global render_ip, render_name, render_url
    render_ip = []
    render_name = []
    render_url = []
    dlnabox.hide()


def on_rbutt_cancelled(agr1, arg2):
    discoverbox.hide()
    return False


def on_rbuttname_clicked(arg1, arg2):
    global defaults
    discoverbox.hide()
    drlabel.set_label('Renderer by name')
    if get_renderer_url('byip'):
        defaults[0] = 3 ## reset settings to DLNA live (!)
        set_gui(defaults)
        return True
    else:
        return False


def on_rbutturl_clicked(arg1, arg2):
    global defaults
    discoverbox.hide()
    drlabel.set_label('Renderer by URL')
    if get_renderer_url('byurl'):
        defaults[0] = 3 ## reset settings to DLNA live (!)
        set_gui(defaults)
        return True
    else:
        return False


# The GUI:
xml = Gtk.Builder()
xml.add_from_file(runpath + 'glade/s2ip_setup_en.ui')

setupwindow = xml.get_object('dialog1')
setupwindow.connect("delete_event", close) #Gtk.main_quit)

SetupIcn = GdkPixbuf.Pixbuf.new_from_file(setupIcon)
setupwindow.set_icon(SetupIcn)
sbutton = xml.get_object('savebutton')
qbutton = xml.get_object('quitbutton')
soq_button = xml.get_object('saveonquit_button')
cos_button = xml.get_object('connectonstart_button')
min_button = xml.get_object('minimize_button')
doq_button = xml.get_object('disconnectonquit_button')
nos_button = xml.get_object('disablesetup_button')
bta_button = xml.get_object('bt_timeout_spin')
auto_button = xml.get_object('autostart_button')
run_button = xml.get_object('runplayer_button')
sqoptions = xml.get_object('sqoptions')
dev_label = xml.get_object('Devices_label')
device = xml.get_object('deviceentry')
player = xml.get_object('mplayerentry')
ip_entrybox = xml.get_object('ip_entry')
ip_label = xml.get_object('ip_label')
fchoose_button = xml.get_object('Filechooser_button')
cmd_entrybox = xml.get_object('command_entry')
status_box = xml.get_object('status_box')

buttonid = sbutton.connect("button-release-event", on_button_clicked)
buttonid = qbutton.connect("button-release-event", on_button_clicked)
buttonid = soq_button.connect("button-release-event", on_button_clicked)
buttonid = cos_button.connect("button-release-event", on_button_clicked)
buttonid = min_button.connect("button-release-event", on_button_clicked)
buttonid = doq_button.connect("button-release-event", on_button_clicked)
buttonid = auto_button.connect("button-release-event", on_button_clicked)
buttonid = run_button.connect("button-release-event", on_button_clicked)
buttonid = fchoose_button.connect("button-release-event", on_button_clicked)
new_iter = device.connect("changed", on_combo_entry_changed)
new_iter = player.connect("changed", on_combo_entry_changed)
new_iter = ip_entrybox.connect("changed", on_ipentry_changed)
new_iter = cmd_entrybox.connect("changed", on_cmdentry_changed)

## Package installation window
installbox = xml.get_object('installbox')
inst_label = xml.get_object('install_label')
butt = ['','','','','', '','','','','', '']
instpic = ['','','','','', '','','','','', '']
for i in range(len(packagelist)):
    butt[i] = xml.get_object('check_'+str(i))
    instpic[i] = xml.get_object('icon_'+str(i))

install_ok = xml.get_object('install_ok')
install_cancel = xml.get_object('install_cancel')
buttonid = install_ok.connect("button-release-event", on_install_clicked)
buttonid = install_cancel.connect("button-release-event", install_cancelled)

## DLNA renderer select window
dlnabox = xml.get_object('dlnabox')
dlna_cancelbutt = xml.get_object('dlna_cancelbutt')
dlna_selectbutt = xml.get_object('dlna_selectbutt')
rbuttonid = dlna_selectbutt.connect("button-release-event", on_dlnaselect_clicked)
rbuttonid = dlna_cancelbutt.connect("button-release-event", dlnaselect_cancelled)
rendererbox = xml.get_object('rendererbox')

## DLNA discover Window
discoverbox = xml.get_object('discover-dialog')
rbuttcancel = xml.get_object('rbutt-cancel')
rbutturl = xml.get_object('rbutt-url')
rbuttname = xml.get_object('rbutt-name')
drlabel = xml.get_object('discover_rendererlabel')
buttonid = rbuttcancel.connect("button-release-event", on_rbutt_cancelled)
buttonid = rbutturl.connect("button-release-event", on_rbutturl_clicked)
buttonid = rbuttname.connect("button-release-event", on_rbuttname_clicked)


def set_gui(settings):
    global ip_label_txt
    print ('SetGUI: ' , settings)
    position = int(settings[0])
    try:
        posplayer = int(settings[14])
    except:
        posplayer = 0
    setupwindow.show_all()
    ip_entrybox.set_text(settings[position + 1])
    cmd_entrybox.set_text(settings[12])
    device_store = Gtk.ListStore(str) # set dropdown for supported devices
    for i in s2ip_methods:
        device_store.append([i['name']]) # = s2ip_methods[i]['name']
    device.set_model(device_store)
    device.set_active(position -2) ## 0,1 deprecated!
    player_store = Gtk.ListStore(str) # set dropdown for supported players
    for j in mplayers:
        player_store.append([j['name']]) # = mplayers[j]['name']
    player.set_model(player_store)
    player.set_active(posplayer) #14 is players
    ip_label.set_text(ip_label_txt[position])
    if position == 4 or position == 6:
        ip_entrybox.hide()
        ip_entrybox.set_text('')
    soq_button.set_active((settings[7] == 'Y')) # save on quit
    cos_button.set_active((settings[8] == 'Y')) # connect on start
    min_button.set_active((settings[9] == 'Y')) # minimize after connect
    doq_button.set_active((settings[10] == 'Y')) # disconnect on quit
    nos_button.set_active((settings[11] == 'Y')) # disable setup
    auto_button.set_active((settings[17] == 'Y')) # add to Startup Apps
    run_button.set_active((settings[18] == 'Y')) # run mplayer on connect
    if settings[13] == 'Y' or settings[13] == 'N' or settings[13] == '?':
        settings[13] = '0'
    bta_button.set_value(int(settings[13])) # autoconnect timeout
    return


def get_buttons(settings):
    if soq_button.get_active(): # save on quit
        settings[7] = 'Y'
    else:
        settings[7] = 'N'
    if cos_button.get_active(): # connect on start
        settings[8] = 'Y'
    else:
        settings[8] = 'N'
    if min_button.get_active(): # minimize after connect
        settings[9] = 'Y'
    else:
        settings[9] = 'N'
    if doq_button.get_active(): # disconnect on quit
        settings[10] = 'Y'
    else:
        settings[10] = 'N'
    if nos_button.get_active(): # no setup
        settings[11] = 'Y'
    else:
        settings[11] = 'N'
    if auto_button.get_active(): # autostart
        settings[17] = 'Y'
    else:
        settings[17] = 'N'
    if run_button.get_active(): # run player
        settings[18] = 'Y'
    else:
        settings[18] = 'N'
    settings[13] = str(bta_button.get_value_as_int()) # autoconnect timeout
    position = settings[0]
    if position == '3': # pulseaudio-dlna need 6s
        if (settings[13] != '0' and int(settings[13]) < 6):
            settings[13] = '6'
    return settings


def check_package(mode): # mode is position of device list
    global packagelist, state
    package_state()
##
    if mode == 2: #UPnP 3
        if packagelist[2]['state'] == 'no' and packagelist[3]['state'] == 'no':
            state[2] = True
            state[3] = True
##
    elif mode == 3: #DLNA live
        if packagelist[10]['state'] == 'no':
            state[10] = True
##
    elif mode == 4: #RTP 01
        if packagelist[0]['state'] == 'no':
            state[0] = True
##
    elif mode == 5: #INet Radio 45
        if packagelist[4]['state'] == 'no':
            state[4] = True  # Icecast2
        if  packagelist[5]['state'] == 'no' and packagelist[6]['state'] == 'no' and packagelist[7]['state'] == 'no':
            state[5] = True  # Darkice
            state[6] = True  # Ices2
            state[7] = True  # Ices
##
    elif mode == 6: #none need no packages
        return True
    if 1 in state:
        for i in range(len(state)):
            if state[i]:
                butt[i].set_active(True)
            else:
                butt[i].set_active(False)
        run_packageinstall()
        if not state:
            return False
    return True

def run_packageinstall():
#    if use_apt:
    installbox.present()
    return

def messagebox(mess_type, title, message):
    self = Gtk.Window()
    dialog = Gtk.MessageDialog(self, 0, mess_type, Gtk.ButtonsType.OK, title)
    dialog.format_secondary_markup(message)
    dialog.run()
    dialog.destroy()


def f_choose(mode): ### File Chooser for Open ###
    if mode == 'Setup':
        discoverbox.present()
        return ''
    dialog = Gtk.FileChooserDialog(None, None, Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
    dialog.set_default_response(Gtk.ResponseType.OK)
    if mode == 'Folder':
        dialog.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
    if mode == 'File':
        dialog.set_action(Gtk.FileChooserAction.OPEN)
    response = dialog.run()
    filename = ''
    if response == Gtk.ResponseType.OK:
        filename = dialog.get_filename()
        if mode == 'Folder':
            filename = filename +'/'
    dialog.destroy()
    return filename


def get_renderer_url(method):
    global defaults, render_ip, render_name, render_url
    discoverbox.hide()
    allrenderers = ''
    allnames = ''
    SSDP_ADDRESS = '239.255.255.250'
    SSDP_PORT = 1900
    MSEARCH = ('M-SEARCH * HTTP/1.1\r\n' + \
              'HOST: {}:{}\r\n'.format(SSDP_ADDRESS, SSDP_PORT) + \
              'MAN: "ssdp:discover"\r\n' + \
              'MX: 2\r\n' + \
              'ST: urn:schemas-upnp-org:device:MediaRenderer:1\r\n\r\n')
    s.setdefaulttimeout(5)
    sock = s.socket(s.AF_INET, s.SOCK_DGRAM, s.IPPROTO_UDP)
    sock.setsockopt(s.IPPROTO_IP, s.IP_MULTICAST_TTL, 10)
    sock.sendto(MSEARCH.encode(), (SSDP_ADDRESS, SSDP_PORT))
    bufsize = 1024
    a = []
    h = []
    render_ip = []
    render_name = []
    render_url = []
    while True:
        try:
            header, address = sock.recvfrom(bufsize)
            a = address[0]
            h = header.lower()
            print (h)
            rendurl = h.decode().split('location: ')[1].split('\r')[0]
            rendip = rendurl.split('http://')[1].split(':')[0]
            with urllib.request.urlopen(rendurl) as f:
                answer = f.read().decode()
            rendername = answer.split('<friendlyName>')[1].split('</friendlyName>')[0]
            print ('[STREAM2IP] DLNA Renderer ' + rendername + ' IP: ' + rendip + 'URL: ' + rendurl)
            render_name += [rendername]
            render_url += [rendurl]
            render_ip += [rendip]
        except: ###
            break
    sock.close()
    if not render_name[0]:
        messagebox(Gtk.MessageType.ERROR, "Could not find any DLNA renderers","Please make sure they are discoverable on searching.")
        return ''
    else:
        dlna_chooser(method)
    return True


def dlna_chooser(method):
    global render_ip, render_name, render_url
    renderer_store = Gtk.ListStore(str) # set dropdown for renderers
    for i in range(len(render_name)):
        renderer_store.append([render_name[i]])
        if method == 'byurl':
            render_ip[i] = ''
    rendererbox.set_model(renderer_store)
    rendererbox.set_active(0)
    dlnabox.present()
    return


def main():
    global defaults, homepath, runpath, setup_runsolo
    setup_runsolo = True
    defaults = load_defaults(homepath)
    print(defaults)
    if admin_mode:
        print('<W> running in administrator mode')
    set_gui(defaults)
    Gtk.main()
    return


def setup(settings):
    global defaults, homepath, runpath, setup_runsolo
    defaults = settings
    setup_runsolo = False
    set_gui(defaults)
    setupwindow.present()
    return defaults


if __name__ == "__main__":
    main()

