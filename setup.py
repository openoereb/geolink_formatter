# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    readme = f.read()
with open(os.path.join(here, 'CHANGELOG')) as f:
    changelog = f.read()

requires = [
    'lxml>=5.3.1',
    'defusedxml',
    'requests',
    'xmlschema'
]

setup(name='geolink_formatter',
      version='2.0.6',
      description='OEREBlex geoLink Formatter',
      license='BSD',
      long_description='{readme}\n\n{changelog}'.format(readme=readme, changelog=changelog),
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 3.9",
          "Programming Language :: Python :: 3.10",
          "Programming Language :: Python :: 3.11",
          "Programming Language :: Python :: 3.12",
          "Topic :: Scientific/Engineering :: GIS",
          "Topic :: Software Development :: Libraries :: Python Modules"
      ],
      author='Karsten Deininger',
      author_email='karsten.deininger@bl.ch',
      url='https://gitlab.com/gf-bl/python-geolink-formatter',
      keywords='oereb lex geolink formatter html',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires
      )
