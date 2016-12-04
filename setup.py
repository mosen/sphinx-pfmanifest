# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

long_desc = '''
This package contains the pfmanifest sphinx extension which reads apple .manifest files and renders a table describing
the manifest.
'''

requires = ['Sphinx>=1.1']

setup(
    name='sphinx-pfmanifest',
    version='0.1',
    url='https://github.com/mosen/sphinx-pfmanifest',
    license='MIT',
    author='mosen',
    author_email='mosen@noreply.users.github.com',
    description='Sphinx Apple Preference Manifest (pfm) Extension',
    long_desc=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: Sphinx :: Extension',
        'Intended Audience :: Developers',
        'Topic :: Documentation :: Sphinx',
    ],
    packages=find_packages(),
    platforms='any',
    install_requires=requires,
)

