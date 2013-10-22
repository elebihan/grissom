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
Miscellaneous functions/classes
"""

import sys
import os
import hashlib
import subprocess
import tempfile
from gettext import gettext as _
from .common import NoMatchError

class SourceCodeFinder(object):
    """Find the source code a binary executable file originated from.

    :param verbose: if True, be more verbose.
    :type verbose: bool
    """
    def __init__(self, verbose=False):
        self._search_paths = []
        self._strip_args = ['strip']
        self._verbose = verbose

    def _set_strip_cmd(self, value):
        self._strip_args = value.split()

    def _get_strip_cmd(self):
        return ' '.join(self._strip_args)

    strip_command = property(_get_strip_cmd,
                             _set_strip_cmd,
                             None,
                             'command for discarding symbols')

    def add_search_path(self, path):
        """Add new a search path for source code.

        :param path: path to directory.
        :type path: str
        """
        self._search_paths.append(path)

    def _check_file_match(self, filename, reference):
        newname = 'grissom-origin-' + os.path.basename(filename)
        tmpname = os.path.join(tempfile.gettempdir(), newname)
        args = [a for a in self._strip_args]
        args.append(filename)
        args.append('-o')
        args.append(tmpname)

        try:
            msg = subprocess.check_output(args,
                                          stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            return False

        with open(tmpname, 'rb') as f:
            if hashlib.sha1(f.read()).hexdigest() == reference:
                matched = True
            else:
                matched = False
        os.unlink(tmpname)
        return matched

    def find_origin_of(self, filename):
        """Find the path to the source code of a file.

        :param filename: path to file to identify.
        :type filename: str

        :returns: the path to the source code directory.
        :rtype: str
        """
        reference = None
        with open(filename, 'rb') as f:
            reference = hashlib.sha1(f.read()).hexdigest()

        filename = os.path.basename(filename)

        for path in self._search_paths:
            for dirpath, dirnames, filenames in os.walk(path):
                for fn in filenames:
                    if fn != filename:
                        continue
                    candidate = os.path.join(dirpath, fn)
                    if self._check_file_match(candidate, reference):
                        return dirpath
                    elif self._verbose:
                        e =_("File does not match: {0}")
                        print(e.format(candidate), file=sys.stderr)

        raise NoMatchError

# vim: ts=4 sts=4 sw=4 et ai
