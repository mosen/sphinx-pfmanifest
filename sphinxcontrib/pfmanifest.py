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


def add_subkey(data):
    """
    Generate documentation for a single key in the manifest.
    Returns a docutils row node.

    :param data: dict item from pfm_subkeys
    :return:
    """
    row = nodes.row()
    subkey_keys = ('pfm_name', 'pfm_type', 'pfm_title', 'pfm_description', 'pfm_require')

    for k in subkey_keys:
        entry = nodes.entry()
        row += entry
        entry += nodes.paragraph(text=data.get(k, 'n/a'))

    return row


class PfmKeyDirective(Directive):
    """
    Directive to render information about a single payload key as a section.

    Example::

        To render information about the payload key "SSID_STR" from a manifest file.

        .. pfm_key:: SSID_STR com.apple.wifi.managed manifest.plist
    """

    required_arguments = 2
    final_argument_whitespace = True

    def run(self):
        warning = self.state.document.reporter.warning
        env = self.state.document.settings.env

        subkey = self.arguments[0]

        fn = search_image_for_language(self.arguments[1], env)
        relfn, absfn = env.relfn2path(fn)
        env.note_dependency(relfn)
        try:
            data = plistlib.readPlist(absfn)
        except IOError as err:
            return [warning('Preference Manifest file "%s" cannot be read: %s'
                            % (fn, err), line=self.lineno)]

        def find_subkey(subkeys, k):
            for d in subkeys:
                if d.get('pfm_name') == k:
                    return d
            return None

        kd = find_subkey(data.get('pfm_subkeys', []), subkey)
        if kd is None:
            return [warning('No pfm_name "%s" exists in manifest "%s".'
                            % (subkey, self.arguments[1]))]

        targetid = "payload-key-%s" % env.new_serialno('payload')
        target = nodes.target('', '', ids=[targetid])

        section = nodes.section()
        section += nodes.title(text=kd.get('pfm_name'))

        return [section]


class PfmDirective(Directive):
    """
    Directive to render a preferences manifest plist as a table.

    Example::

        .. pfm:: test.manifest

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

        table = nodes.table()
        payload_type = nodes.emphasis('', pfmanifestdata.get('pfm_domain'))
        title = nodes.title()
        table += title

        title += payload_type
        title += nodes.paragraph(text=pfmanifestdata.get('pfm_description'))

        header = ('Name', 'Type', 'Title', 'Description', 'Required')

        tgroup = nodes.tgroup(cols=len(header))
        table += tgroup

        colwidths = (1, 1, 1, 3, 1)
        for colwidth in colwidths:
            tgroup += nodes.colspec(colwidth=colwidth)

        thead = nodes.thead()
        tgroup += thead

        th_row = nodes.row()
        thead += th_row

        for head in header:
            entry = nodes.entry()
            th_row += entry
            entry += nodes.paragraph(text=head)

        tbody = nodes.tbody()
        tgroup += tbody


        rows = [add_subkey(subkey) for subkey in pfmanifestdata.get('pfm_subkeys')]
        tbody += rows
        #tbody = nodes.tbody('', *rows)





        return [table]


def setup(app):
    app.add_directive('pfm', PfmDirective)
    app.add_directive('pfm_key', PfmKeyDirective)

    return {'version': '0.1'}