#!/usr/bin/env python
import pathlib

from setuptools import setup, find_packages
from uim import __version__

import sys
CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 6)

# This check and everything above must remain compatible with Python 3.6.
if CURRENT_PYTHON < REQUIRED_PYTHON:
    sys.stderr.write(f"""
    ==========================
    Unsupported Python version
    ==========================
    This version of Universal Ink Library requires Python {REQUIRED_PYTHON}.{CURRENT_PYTHON}, but you're trying to
    install it on Python {REQUIRED_PYTHON}.{CURRENT_PYTHON}.
    This may be because you are using a version of pip that doesn't
    understand the python_requires classifier. Make sure you
    have pip >= 9.0 and setuptools >= 24.2, then try again:
        $ python -m pip install --upgrade pip setuptools
        $ python -m pip install uim-lib
    This will install the latest version of UIM lib which works on your
    version of Python. 
    """)
    sys.exit(1)

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# the setup
setup(
    name='universal_ink_library',
    version=__version__,
    description='Library to parse and write Universal Ink Model data files.',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/Wacom-Developer/universal-ink-library',
    author='Markus Weber',
    author_email='markus.weber@wacom.com',
    license='Apache 2.0 License',
    keywords='universal ink model;digital ink;wacom ink technologies',
    packages=find_packages(exclude=('docs', 'tests', 'env')),
    include_package_data=True,
    install_requires=[
        "numpy>=1.16.4",
        "bitstring>=3.1.7",
        "protobuf>=3.15.3",
        "varint>=1.0.2",
        "python-dateutil>=2.8.1",
        "lxml>=4.6.3"
    ],
    extras_require={
    },
    tests_require=(
        'pytest',
        'pytest-mock',
        'pytest-cov'
    ),
    classifiers=[
        # Status
        'Development Status :: 3 - Alpha',
        # Audience
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        # Python Version
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
    )
