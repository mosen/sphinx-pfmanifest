# -*- coding: utf-8 -*-
"""
    sphinxcontrib.pfmanifest
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Generate tables from apple preference manifests.

    :license: MIT
"""

import os.path
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.errors import SphinxError
import plistlib

try:
    from sphinx.util.i18n import search_image_for_language
except ImportError:  # Sphinx < 1.4
    def search_image_for_language(filename, env):
        return filename


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
        headings = ('Type', 'Default', 'Required', 'Regex', 'iOS', 'macOS', 'Supervised')
        table = nodes.table()

        tgroup = nodes.tgroup(cols=len(headings))
        table += tgroup

        colwidths = (1, 1, 1, 1, 1, 1, 1)
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

        keys = ('pfm_type', 'pfm_default', 'pfm_require', 'pfm_format', 'pfm_ios_min', 'pfm_macos_min', 'pfm_supervised')
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

class PfmHeaderDirective(Directive):
    """
    Directive to render top level key values as a definition list.

    Example::

        .. pfmheader:: test.manifest

    """
    has_content = False
    required_arguments = 1
    final_argument_whitespace = True

    header_keys = ('pfm_domain', 'pfm_supervised', 'pfm_macos_min', 'pfm_macos_max', 'pfm_ios_min', 'pfm_ios_max',
                   'pfm_unique')
    headers = {
        'pfm_domain': 'PayloadType',
        'pfm_supervised': 'Supervised Only',
        'pfm_macos_min': 'macOS',
        'pfm_macos_max': 'macOS Deprecated',
        'pfm_ios_min': 'iOS',
        'pfm_ios_max': 'iOS Deprecated',
        'pfm_unique': 'Highlander'
    }

    def field_list_item(self, label, value):
        field = nodes.field()
        field += nodes.field_name(text=label)
        fb = nodes.field_body()
        field += fb
        fb += nodes.paragraph(text=value)
        return field

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

        fl = nodes.field_list()

        for k in self.header_keys:
            if k in pfmanifestdata:
                fl += self.field_list_item(self.headers[k], pfmanifestdata.get(k, 'N/A'))
            else:
                fl += self.field_list_item(self.headers[k], 'N/A')

        return [fl]

class PfmDirective(Directive):
    """
    Directive to render a preferences manifest plist as a table.

    Example::

        .. pfm:: test.manifest
           :key: subkey.subsubkey
           :include_common:
    """
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        'key': lambda v: [k for k in v.split()],
        'include_common': directives.flag
    }
    common_keys = ('PayloadDescription', 'PayloadDisplayName', 'PayloadIdentifier', 'PayloadType', 'PayloadUUID',
                   'PayloadVersion', 'PayloadOrganization')

    def rows(self, dicts):
        """
        Generate documentation table rows for a collection of keys
        Yields a docutils row node

        :param data: dict item from pfm_subkeys
        :return:
        """
        for d in dicts:
            if d['pfm_name'] in self.common_keys:
                continue

            row = nodes.row()
            subkey_keys = ('pfm_name', 'pfm_type', 'pfm_title', 'pfm_description', 'pfm_require')

            for sk in subkey_keys:
                entry = nodes.entry()
                row += entry
                entry += nodes.paragraph(text=d.get(sk, 'n/a'))

            yield row


    def get_subkey(self, root, subkeys):
        """
        Traverse the manifest structure to get a nested list of subkeys

        :param root: The root of the manifest data
        :param subkeys: Array of key pfm_name's to traverse
        :return: dict pfm_subkey value after traversing, or None if it doesn't exist
        """
        subkey = subkeys.pop(0)

        for element in root:
            if 'pfm_name' not in element:
                continue  # skip bad elements that have no name

            if element.get('pfm_name') == subkey:
                if len(subkeys) == 0:
                    return element
                else:
                    if 'pfm_subkeys' not in element:
                        raise self.error('Trying to access subkey {} of {}, doesnt exist.'.format(subkey, element.get('pfm_name')))
                    else:
                        return self.get_subkey(element.get('pfm_subkeys'), subkeys)

        return None

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

        if len(self.options.get('key', [])) > 0:
            pfmanifestdata = self.get_subkey(pfmanifestdata.get('pfm_subkeys'), self.options['key'])
            if pfmanifestdata is None:
                raise self.severe("Could not locate the manifest key specified by: {}".format(self.options['key']))

        rows = [row for row in self.rows(pfmanifestdata.get('pfm_subkeys'))]
        tbody += rows
        #tbody = nodes.tbody('', *rows)

        return [table]


def setup(app):
    app.add_directive('pfm', PfmDirective)
    app.add_directive('pfmheader', PfmHeaderDirective)
    app.add_directive('pfmkey', PfmKeyDirective)

    return {'version': '0.1'}