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
Binary executable files core classes.
"""

import os
import re
import stat
import magic
from ..common import FileNotFoundError
from gettext import gettext as _

class BinfmtInspector(object):
    """Base class for inspecting binary executable files.

    :param filename: path to the executable/library file to inspect.
    :type filename: str
    """
    def __init__(self, filename):
        self._filename = filename
        self._lib_paths = []
        self._with_full_path = False

    def add_library_path(self, path):
        """Add a new search path for libraries.

        :param path: new path to look into.
        :type path: str
        """
        self._lib_paths.append(path)

    def find_dependencies(self, recursive=False):
        """Find the dependencies of the binary executable file.

        :param recursive: if true, perform a recursive search.
        :type recursive: bool

        :returns: an acyclic directed graph as an adjacent list
        """
        return []

    def _get_abs_path(self, filename):
        if os.path.isabs(filename):
            return filename
        for path in self._lib_paths:
            fullname = os.path.join(path, filename)
            if os.path.exists(fullname):
                return fullname
        else:
            msg = _("can not find '{fn}").format({'fn': filename})
            raise FileNotFoundError(msg)

    def _set_with_full_path(self, value):
        self._with_full_path = value

    def _get_with_full_path(self):
        return self._with_full_path

    with_full_path = property(_get_with_full_path, _set_with_full_path)

class BinfmtFinder(object):
    """Find binary executable files/libraries

    :param include_libs: if true, will also look for shared libraries
    :type include_libs: bool

    :param include_kmods: if true, will also look for kernel modules
    :type include_libs: bool
    """
    def __init__(self, include_libs=False, include_kmods=False):
        self._include_libs = include_libs
        self._include_kmods = include_kmods

    def scan(self, directory):
        """Scan a directory.

        :param directory: path to directory to scan.
        :type directory: str

        :returns: paths to binary executable files.
        :rtype: list of strings
        """
        results = []
        for root, dirs, files in os.walk(directory):
            for f in files:
                filename = os.path.join(root, f)
                mode = os.lstat(filename).st_mode
                if stat.S_ISLNK(mode):
                    continue
                if not is_binfmt_file(filename):
                    continue
                r, ext = os.path.splitext(filename)
                if ext in ('.o', '.a'):
                    continue
                if ext == '.ko' and self._include_kmods:
                    results.append(filename)
                elif ext == '.so' and self._include_libs:
                    results.append(filename)
                elif ext == '' and mode & stat.S_IXUSR:
                    results.append(filename)
        return results

_BINFMT_MAGIC_PATTERNS = (
    r'^ELF',
)

def is_binfmt_file(filename):
    """Check if filename points to a binary executable file/shared library.

    :param filename: path to the file.
    :type filename: str

    :returns: True or False.
    :rtype: bool
    """
    with magic.Magic() as m:
        text = m.id_filename(filename)
        for pattern in _BINFMT_MAGIC_PATTERNS:
            if re.match(pattern, text):
                return True
    return False

# vim: ts=4 sts=4 sw=4 et ai
