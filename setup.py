#!/usr/bin/python3

from distutils.core import setup
import sys, os

setup(name='stream2ip',
    author='Takkat Nebuk',
    author_email='takkat.nebuk@gmail.com',
    url='https://github.com/Takkat-Nebuk/stream2ip',
    license='gpl',
    description='Setup audio network streams',
    version='1.1.6',
    packages=['stream2ip-gtk3'],
    package_data={
        '':['glade/*.ui', 'icons/*.svg', 'darkice-s2ip.cfg', 'ices-s2ip.conf', 'ices-s2ip.xml', 'icecast.xml']
        },
    data_files=[('',
                   ["data/stream2ip.desktop"]),
                 ],
    scripts=['stream2ip']
)

