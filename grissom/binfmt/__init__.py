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
Binary executable file handling
"""

import magic
import re
from gettext import gettext as _
from ..common import InvalidFormatError
from .elf import ElfInspector

_BINFMT_INSPECTORS = {r'^ELF': ElfInspector}

def create_inspector(filename):
    with magic.Magic() as m:
        text = m.id_filename(filename)
        for pattern, klass in _BINFMT_INSPECTORS.items():
            if re.match(pattern, text):
                return klass(filename)
    raise InvalidFormatError(_("File format not supported"))

# vim: ts=4 sts=4 sw=4 et ai
