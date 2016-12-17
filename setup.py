# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

long_desc = '''
This package contains the pfmanifest sphinx extension which reads apple .manifest files and renders a table describing
the manifest.
'''

requires = ['Sphinx>=1.1']

setup(
    name='pfmanifest',
    version='0.1',
    url='https://github.com/mosen/sphinx-pfmanifest',
    license='MIT',
    author='mosen',
    author_email='mosen@noreply.users.github.com',
    description='Sphinx Apple Preference Manifest (pfm) Extension',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: Sphinx :: Extension',
        'Intended Audience :: Developers',
        'Topic :: Documentation :: Sphinx',
    ],
    keywords="apple mobileconfig manifest sphinx extension",
    packages=find_packages(exclude=["tests"]),
    platforms='any',
    namespace_packages=['sphinxcontrib'],
    install_requires=requires,
)

