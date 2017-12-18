#!/usr/bin/env python

from setuptools import setup, find_packages
import os.path
import sys

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as f:
    long_description = f.read()

setup(
    name='FeenICS',
    version='0.1',
    author='Erika Ziraldo',
    long_description=long_description,
    description='For cleaning spiral scans containing spiral specific artifact',
    url='https://github.com/eziraldo/FeenICS',
    scripts=['bin/s1_folder_setup.py','bin/s2_identify_components.py', 'bin/s3_remove_flagged_components.py', 'bin/check_slices.py'],
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


setup(
    name='FeenICS',
    version='0.1',
    description='For cleaning spiral scans containing spiral specific artifact',
    long_description=long_description,
    url='https://github.com/eziraldo/FeenICS',
    author='Erika Ziraldo',
    author_email='eziraldo@uoguelph.ca',
    license='MIT',
    classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: MIT License',
            'Natural Language :: English',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3'],
    keywords='spiral neuroimaging fMRI artifact',
    packages=find_packages(),
    data_files=[('', ['README.md'])],
    entry_points={
        'console_scripts': [
            's1_folder_setup.py=FeenICS.bin.s1_folder_setup.py:main',
            's2_identify_components.py=FeenICS.bin.s2_identify_components.py:main',
            's3_remove_flagged_components.py=FeenICS.bin.s3_remove_flagged_components.py:main',
            'check_slices.py=FeenICS.bin.check_slices.py:main'
        ],
    },
    scripts=['bin/s1_folder_setup.py','bin/s2_identify_components.py', 'bin/s3_remove_flagged_components.py', 'bin/check_slices.py'],
    install_requires=[
            'matplotlib',
            'nibabel',
            'numpy',
            'pandas',
            'scipy',
            'scikit-image>=0.13.1'],
    include_package_data=True,
)
