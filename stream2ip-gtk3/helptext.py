help_intro_txt = '''
<b><span size="xx-large">Stream2ip</span></b>\n\n
<i>Designed to provide audio streams through your network.</i>\n
\n
For a more concise help visit the stream2ip online help
by clicking <i>Get Help Online</i> below to visit
<b>http://stream2ip.takkat.de</b>\n in your browser.
'''

help_general_txt = '''
<b><big>General Setup</big></b>\n
\n
On first run please go to <i>Preferences</i> to choose the desired
streaming method from the <b>Devices</b> menu. Give in settings on
the line next to there. Settings depend on the streaming method chosen.
\n
For some media players tag infos can be displayed. Choose a player
to be watched for this.
\n
Additional packages needed will be prompted for installation.
'''

help_airport_txt = '''
<b><big>Airport Express (discontinued)</big></b>\n
<small><i>Airport Express (1st Gen Air Tunes) devices are no longer supported.</i>
\n
</small>'''

help_bluetooth_txt = '''
<b><big>Bluetooth Audio Devices (discontinued)</big></b>\n
<small>Connecting to Bluetooth auido devices is no longer supported\n
\n
</small>'''

help_upnp_txt = '''
<b><big>UPnP/DNLA</big></b>\n
<small>We can use miniDLNA/readyMedia or uShare for providing media data 
to acess via DLNA. Stream2ip decides on the settings which program to choose. 
Take care that this application is installed.
\n
<b>miniDLNA</b> has a config file <tt>minidlna.conf</tt> in <tt>~/.config/stream2ip</tt> where
media directories are defined.
<b>uShare</b> accepts a blank separated list of paths to media. A single media directory can be 
added from a file chooser.
\n
<b>Example settings:</b>
<tt><span background="white"> minidlna </span></tt>  -  <small>will run miniDLNA</small>
<tt><span background="white"> /path/to/media1 /path/to/media2 </span></tt>  -  <small>will run uShare.</small>
</small>'''

help_dlnalive_txt = '''
<b><big>DLNA live</big></b>\n
<small>to push the audio output to a DLNA renderer in our network by using
<b>pulseaudio-dlna</b> (available after <b>ppa:qos/pulseaudio-dlna</b> was 
added to our sources).
\n
We can give in a stream URL or a named device to connect to. The preferences
dialog lets us search for a running renderer.
Additional parameters can be given in <tt>~/.config/stream2ip/padlna.cfg.</tt>
\n
<b>Example settings:</b>
<tt><span background="white"> BubbleUPnP (GT-I9000)@192.168.178.53 </span></tt>  -  connecting by name.
<tt><span background="white"> http://192.168.178.24:7676/smp_18_</span></tt>  -  connecting by URL.
<tt><span background="white">  --stream-urls [URL] --port 8081 --encoder ogg</span></tt>  -  full command set
</small>'''

help_inetradio_txt = '''
<b><big>Internet Radio</big></b>\n
<small>We can provide an Icecast Internet radio stream in our network. Default
configuration files may need to be adapted to our environment.
By default Icecast runs system-wide. Stream2ip will start an Icecast server 
in user-space if Icecast was not running.
\n
To stream the live audio in mp3 use <b>Darkice</b> which can be configured in
<tt>~/.config/stream2ip/darkice-s2ip.cfg</tt>. Give in <tt>live</tt> in the
settings line.
In case we want OGG streams we can use <b>Ices2</b>. Give in the configuration
file with <tt>.xml</tt> extension in the settings line. By this we will also be
able to stream OGG playlists.
Mp3-playlists can be streamed using <b>Ices</b>. This expects a path to the 
playlist with <tt>.m3u</tt> extension in the settings line.
\n
<b>Example settings:</b>
<tt><span background="white"> live </span></tt>  - stream live audio
<tt><span background="white"> /path/to/myplaylist.m3u </span></tt>  - playlist with mp3
<tt><span background="white"> /path/to/settings.xml </span></tt>  - uses Ices2 with given settings.
</small>'''






