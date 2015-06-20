from setuptools import setup

APP = ['Solitaire.py']
DATA_FILES = [ ('',['images'])]
OPTIONS = {}

setup(
	app = APP,
	data_files = DATA_FILES,
	options = {'p2app': OPTIONS},
	setup_requires = ['py2app'],
)
