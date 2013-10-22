# -*- coding: utf-8 -*-
#
# grissom - FOSS compliance tools
#
# Copyright (c) 2013 Eric Le Bihan <eric.le.bihan.dev@free.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Common functions/classes
"""

import configparser
import subprocess
import mimetypes
import random
import sys
import os
from gettext import bindtextdomain, textdomain
from gettext import gettext as _


class InvalidFormatError(Exception):
    """Error raised when file format is not supported"""

class FileNotFoundError(Exception):
    """Error raised when a file is not found"""

class NoMatchError(Exception):
    """Error raised when a file does match a criterium"""

class ToolNotFoundError(Exception):
    """Error raised when an external tool can not be found"""

def topological_sort(graph_unsorted):
    """Perform a topological sort on a mapping between an item and its
    depedencies.

    :param graph_unsorted: acyclic graph to sort
    :type graph_unsorted: mapping between a string and a list of strings.

    :returns: a list of (node, edges) tuples
    """

    graph_sorted = []

    while graph_unsorted:
        acyclic = False
        for node, edges in list(graph_unsorted.items()):
            for edge in edges:
                if edge in graph_unsorted:
                    break
            else:
                acyclic = True
                del graph_unsorted[node]
                graph_sorted.append((node, edges))
        if not acyclic:
            raise RuntimeError("Not an acyclic graph")

    return graph_sorted

def load_configuration():
    """Load configuration from the user configuration file.

    :returns: the configuration.
    :rtype: :class:`configparser.ConfigParser`.
    """
    filename = os.path.expanduser('~/.config/grissom.conf')
    if not os.path.exists(filename):
        raise FileNotFoundError("Configuration file not found")

    parser = configparser.ConfigParser()
    parser.readfp(open(filename))
    return parser

def encode_multipart_formdata(variables, files):
    """Encode variables and files for uploading.

    :param variables: regular form variables.
    :type variables: sequence of (name, value) elements.

    :param files: files to be encoded.
    :type files: list of file-like objects

    :returns: the content-type and body to be sent.
    :rtype: tuple of strings.
    """
    token = random.randrange(sys.maxsize)
    boundary = '--' * 15 + "{0:x}".format(token)
    lines = []

    for k, v in variables:
        lines.append(bytes("--{0}".format(boundary), 'utf-8'))
        l = "Content-Disposition: form-data; name=\"{0}\"".format(k)
        lines.append(bytes(l, 'utf-8'))
        lines.append(b'')
        lines.append(bytes(v, 'utf-8'))

    for k, n, v in files:
        filetype = mimetypes.guess_type(n)[0] or 'application/octet-stream'
        lines.append(bytes("--{0}".format(boundary), 'utf-8'))
        l = "Content-Disposition: form-data; name=\"{0}\"; filename=\"{1}\""
        lines.append(bytes(l.format(k, n), 'utf-8'))
        lines.append(bytes("Content-Type: {0}".format(filetype), 'utf-8'))
        lines.append(b'')
        lines.append(v)

    lines.append(bytes("--{0}--".format(boundary), 'utf-8'))
    lines.append(b'')
    body = b'\r\n'.join(lines)
    contenttype = "multipart/form-data; boundary={0}".format(boundary)
    return contenttype, body

__archive_mimetypes = (
    'application/x-tar',
    'application/x-compressed-tar',
    'application/x-bzip-compressed-tar',
    'application/x-xz-compressed-tar',
    'application/zip'
)

def is_compressed_archive(filename):
    """Return true if file is a compressed archive.

    :param filename: path to the file to test.
    :type filename: str

    :returns: true if the file is a compressed archive.
    :rtype: bool
    """
    ft = mimetypes.guess_type(filename)[0]
    if ft in __archive_mimetypes:
        return True
    return False

def sanitize_args(args):
    """Sanitize argument list.

    :param args: list of arguments
    :type args: list of str

    :returns: the sanitized arguments.
    :rtype: list of str.

    This function check if argument list is to be read from standard input
    or not.
    """
    if args[0] == '-':
        return map(lambda l: l.strip(), sys.stdin)
    else:
        return args

def execute_command(args):
    """Execute an external progam.

    :param args: list of arguments.
    :type args: list of str.
    """
    try:
        proc = subprocess.Popen(args,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        proc.wait()
    except OSError:
        raise ToolNotFoundError(_("Can not find {0}").format(args[0]))

def setup_i18n():
    """Set up internationalization."""
    if hasattr(sys, 'frozen'):
        root_dir = os.path.dirname(sys.executable)
    else:
        root_dir = os.path.dirname(os.path.abspath(__file__))
    if 'lib' not in root_dir:
        return
    root_dir, mod_dir = root_dir.split('lib', 1)
    locale_dir = os.path.join(root_dir, 'share', 'locale')

    bindtextdomain('grissom', locale_dir)
    textdomain('grissom')


# vim: ts=4 sts=4 sw=4 et ai
