from setuptools import setup, find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name="inverutils",
	packages=find_packages() ,
	version="1.0.1", 
	descrription="Tools for investing portfolio", 
	long_description = long_description,
	long_description_content_type = "text/markdown",
	author="Tomas Juan Galizia",
	author_email="xtom4s@gmail.com", 
	url="https://github.com/xtom4s/inverutilities",
	keywords="" ,
	classifiers=["Programming Language :: Python :: 3","License :: OSI Approved :: MIT License","Operating System :: OS Independent"],
	install_requires=["pandas","datetime","requests"])
