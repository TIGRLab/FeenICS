#!/usr/bin/env python

from setuptools import setup, find_packages
import os.path
import sys

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as f:
    long_description = f.read()

setup(
    name='FeenICS',
    version='1.0',
    author='Erika Ziraldo',
    long_description=long_description,
    description='For cleaning spiral scans containing spiral specific artifact',
    url='https://github.com/eziraldo/FeenICS',
    scripts=["bin/s1_folder_setup.py","bin/s2_identify_components.py", "bin/s3_remove_flagged_components.py", "bin/check_slices.py"],
    setup_requires=['numpy','nibabel','matplotlib','scipy','scikit-image>=0.13'],
    classifiers=[
       'Environment :: Console',
       'Intended Audience :: Science/Research',
       'License :: OSI Approved :: MIT License',
       'Natural Language :: English',
       'Operating System :: POSIX :: Linux',
       'Programming Language :: Python :: 2',
       'Programming Language :: Python :: 3'
    ],
)