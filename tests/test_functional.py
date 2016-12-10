from __future__ import print_function
import glob
import os
import re
import tempfile
import shutil

from sphinx.application import Sphinx

from nose.tools import *

# With apologies to sphinxcontrib-plantuml


_fixturedir = os.path.join(os.path.dirname(__file__), 'fixture')


def setup():
    global _tempdir, _srcdir, _outdir
    _tempdir = tempfile.mkdtemp()
    _srcdir = os.path.join(_tempdir, 'src')
    _outdir = os.path.join(_tempdir, 'out')
    os.mkdir(_srcdir)
    shutil.copyfile(
        os.path.join(_fixturedir, 'com.apple.fontmanifest.plist'),
        os.path.join(_srcdir, 'com.apple.fontmanifest.plist')
    )


def teardown():
    shutil.rmtree(_tempdir)


def readfile(fname):
    f = open(os.path.join(_outdir, fname), 'rb')
    try:
        return f.read()
    finally:
        f.close()


def runsphinx(text, builder):
    print('writing text')
    f = open(os.path.join(_srcdir, 'index.rst'), 'wb')
    try:
        f.write(text.encode('utf-8'))
    finally:
        f.close()

    app = Sphinx(_srcdir, _fixturedir, _outdir, _outdir, builder)
    app.build()


def with_runsphinx(builder, **kwargs):
    def wrapfunc(func):
        def test():
            src = '\n'.join(l[4:] for l in func.__doc__.splitlines()[2:])
            os.mkdir(_outdir)

            try:
                runsphinx(src, builder)
                func()
            finally:
                os.unlink(os.path.join(_srcdir, 'index.rst'))
                shutil.rmtree(_outdir)

        test.__name__ = func.__name__
        return test

    return wrapfunc


@with_runsphinx('html')
def test_buildhtml_manifest_font():
    """Generate simple HTML from font payload preferences manifest.

    .. pfm:: com.apple.fontmanifest.plist
    """
    content = readfile('index.html')
    print(content)
