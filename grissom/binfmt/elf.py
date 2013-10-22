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
Executable and Linkable Format
"""

import os
from elftools.common.py3compat import bytes2str
from elftools.common.exceptions import ELFError
from elftools.elf.elffile import ELFFile
from elftools.elf.dynamic import DynamicSection
from .core import BinfmtInspector

class ElfInspector(BinfmtInspector):
    """Inspect ELF files.

    :param filename: path to the ELF file.
    :type filename: str
    """
    def __init__(self, filename):
        BinfmtInspector.__init__(self, filename)

    def find_dependencies(self, recursive=False):
        """Find the dependencies of the ELF file.

        :param recursive: if true, perform a recursive search.
        :type recursive: bool

        :returns: an acyclic directed graph as an adjacent list
        """
        return self._find_deps(self._filename, recursive)

    def _find_deps(self, filename, recursive):
        libs = []
        filename = self._get_abs_path(filename)
        with open(filename, 'rb') as f:
            try:
                elf = ELFFile(f)
                for section in elf.iter_sections():
                    if not isinstance(section, DynamicSection):
                        continue
                    for tag in section.iter_tags():
                        if tag.entry.d_tag == 'DT_NEEDED':
                            lib = bytes2str(tag.needed)
                            libs.append(lib)
            except ELFError:
                raise

        if self._with_full_path:
            libs = [self._get_abs_path(l) for l in libs]
            deps = [(filename, libs)]
        else:
            deps = [(os.path.basename(filename), libs)]

        if recursive:
            for lib in libs:
                deps += self._find_deps(lib, recursive)
        return deps

# vim: ts=4 sts=4 sw=4 et ai
