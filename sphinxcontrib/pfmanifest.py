# -*- coding: utf-8 -*-
"""
    sphinxcontrib.pfmanifest
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Generate tables from apple preference manifests.

    :license: MIT
"""

import os.path
from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.errors import SphinxError
import plistlib

try:
    from sphinx.util.i18n import search_image_for_language
except ImportError:  # Sphinx < 1.4
    def search_image_for_language(filename, env):
        return filename


# def visit_pfmanifest_html(self, node):
#     pass
#
# def depart_pfmanifest_html(self, node):
#     pass
#
#
# class pfmanifest(nodes.General, nodes.Element):
#     pass


def generate_key(keydata):
    """
    Generate documentation for a single key in the manifest.
    :param keydata:
    :return:
    """

    row = nodes.row()
    return row


class PfmanifestDirective(Directive):
    """
    Directive to insert a preferences manifest table.

    Example::

        .. pfmanifest:: test.manifest

    """
    has_content = False
    required_arguments = 1

    def run(self):
        warning = self.state.document.reporter.warning
        env = self.state.document.settings.env
        fn = search_image_for_language(self.arguments[0], env)
        relfn, absfn = env.relfn2path(fn)
        env.note_dependency(relfn)
        try:
            pfmanifestdata = plistlib.readPlist(absfn)
        except IOError as err:
            return [warning('Preference Manifest file "%s" cannot be read: %s'
                            % (fn, err), line=self.lineno)]

        from pprint import pprint
        pprint(pfmanifestdata)

        colspec_a = nodes.colspec('', colwidth=10)
        thead = nodes.thead('')


        tbody = nodes.tbody('')

        tgroup = nodes.tgroup('', colspec_a, thead, tbody)

        table = nodes.table('', tgroup)
        table.attributes['class'] = 'asd'
        return [table, table]


def setup(app):
    # No need to create a pfmanifest node because we will just generate docutils nodes.
    # app.add_node(pfmanifest,
    #              html=(visit_pfmanifest_html, depart_pfmanifest_html))
    app.add_directive('pfmanifest', PfmanifestDirective)

    return {'version': '0.1'}