#!/usr/bin/env python3
from setuptools import setup, find_packages
import os
import sys

webapp = []
for x in os.walk("web"):
    webapp.append((os.path.join('/usr/share/orthogonalspace', x[0]), [os.path.join(x[0], y) for y in x[2]]))

setup(
    name='orthogonalspace',
    packages=find_packages(exclude=['etc', 'contrib']),
    version='0.0.1',
    description='Space-based game',
    long_description="""Fly a ship with friends.""",
    license="GPLv3",
    author='Dylan Whichard',
    author_email='dylan@hackafe.net',
    url='https://github.com/umbc-hackafe/orthogonalspace',
    keywords=[
        'game',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: No Input/Output (Daemon)',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
    ],
    install_requires=[
        'docopt',
        'autobahn>=0.9.1',
        'crossbar',
        'SQLAlchemy',
        'passlib',
    ],
    data_files=[
        ('/usr/lib/systemd/system/', ['contrib/orthogonalspace.service']),
        ('/var/orthogonalspace/', ['contrib/crossbar/config.json']),
        ('/var/orthogonalspace/', []),
        ('/etc/orthogonalspace/', []),
        ('/usr/lib/orthogonalspace/', ['contrib/conf.json']),
    ]+webapp,
)
