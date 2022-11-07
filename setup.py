from setuptools import setup, find_packages

setup(name="inverutils",
	packages=find_packages() ,
	version="1.0.1", 
	description="Tools for tracking investing portfolio", 
	author="Tomas Juan Galizia",
	author_email="xtom4s@gmail.com", 
	url="https://github.com/xtom4s/inverutilities",
	classifiers=["Programming Language :: Python :: 3","License :: OSI Approved :: MIT License","Operating System :: OS Independent"],
	install_requires=["requests", "pandas", "datetime"]) # For some reason it fails with "time" inside, so it is removed as it is a built-in module
