"""
Script for building SolitaireDJ.

Usage:
    python setup.py py2app
"""
from setuptools import setup

NAME = 'SolitaireDJ'
VERSION = '0.1'

plist = dict(
    CFBundleIconFile=NAME,
    CFBundleName=NAME,
    CFBundleShortVersionString=VERSION,
    CFBundleGetInfoString=' '.join([NAME, VERSION]),
    CFBundleExecutable=NAME,
    CFBundleIdentifier='org.pygame.solitairedj',
)

setup(
    data_files=['data'],
    app=[
        dict(script="Solitaire.py", plist=plist),
    ],
    setup_requires=["py2app"],
)
