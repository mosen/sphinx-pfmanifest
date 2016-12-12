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

        .. pfmkey::SSID_STR com.apple.wifi.managed manifest.plist

    TODO: pfm_conditionals.pfm_target_conditions (only enabled when these conditions are met)
    TODO: pfm_exclude
    TODO: pfm_require "push", "always"
    """

    required_arguments = 2
    final_argument_whitespace = True
    has_content = False

    def build_spec_table(self, data):
        """
        Build a table including the data type, format required, etc of this key.
        :return: nodes.table
        """
        headings = ('Type', 'Default', 'Required', 'Regex')
        table = nodes.table()

        tgroup = nodes.tgroup(cols=len(headings))
        table += tgroup

        colwidths = (1, 1, 1, 1)
        for colwidth in colwidths:
            tgroup += nodes.colspec(colwidth=colwidth)

        thead = nodes.thead()
        tgroup += thead

        th_row = nodes.row()
        thead += th_row

        for head in headings:
            entry = nodes.entry()
            th_row += entry
            entry += nodes.paragraph(text=head)

        tbody = nodes.tbody()
        tgroup += tbody

        tdrow = nodes.row()
        tbody += tdrow

        keys = ('pfm_type', 'pfm_default', 'pfm_require', 'pfm_format')
        for k in keys:
            entry = nodes.entry()
            entry += nodes.paragraph(text=data.get(k, 'N/A'))
            tdrow += entry

        return table

    def build_choice_list(self, pfm_range_list):
        """
        Build a list containing possible value choices from `pfm_range_list`.
        :param data:
        :return:
        """
        choices = nodes.bullet_list()
        for choice in pfm_range_list:
            item = nodes.list_item()
            p = nodes.paragraph(text=choice)
            item += p
            choices += item

        return choices


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

        targetid = "{0}-{1}-{2}".format(data.get('pfm_domain', 'pref.domain.na'), kd.get('pfm_name'), 'auto')
        section = nodes.section(ids=[targetid])

        section += nodes.title(text=kd.get('pfm_name', 'key name'))
        section += nodes.paragraph(text=kd.get('pfm_title', 'Title not available'))
        section += nodes.paragraph(text=kd.get('pfm_description', 'Description not available'))
        section += self.build_spec_table(kd)

        if 'pfm_range_list' in kd:
            section += nodes.title(text='Valid Choices')
            section += self.build_choice_list(kd['pfm_range_list'])

        # if 'pfm_subkeys' in kd:
        # recursive render

        return [section]


class PfmDirective(Directive):
    """
    Directive to render a preferences manifest plist as a table.

    Example::

        .. pfm:: test.manifest

    """
    has_content = False
    required_arguments = 1
    final_argument_whitespace = True

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

        header_dl = nodes.definition_list()
        payload_type_item = nodes.definition_list_item()
        header_dl += payload_type_item
        payload_type_item += nodes.term('', 'PayloadType')
        payload_type_def = nodes.definition()
        payload_type_item += payload_type_def
        payload_type_def += nodes.paragraph(text=pfmanifestdata.get('pfm_domain'))

        table = nodes.table()
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

        skip_names = ('PayloadDescription', 'PayloadDisplayName', 'PayloadIdentifier')
        rows = [add_subkey(subkey) for subkey in pfmanifestdata.get('pfm_subkeys')]
        tbody += rows
        #tbody = nodes.tbody('', *rows)

        return [header_dl, table]


def setup(app):
    app.add_directive('pfm', PfmDirective)
    app.add_directive('pfmkey', PfmKeyDirective)

    return {'version': '0.1'}