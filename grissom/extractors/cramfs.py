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

import os
from .core import Extractor
from ..common import execute_command

class CramfsExtractor(Extractor):
    """Extract data from a Linux Compressed ROM File System."""
    def __init__(self, filename):
        Extractor.__init__(self, filename)
        self._desc = 'CRAMFS'

    def extract(self, destination):
        if not os.path.exists(destination):
            os.makedirs(destination)
        root, ext = os.path.splitext(os.path.basename(self._filename))
        destination = os.path.join(destination, root)
        args = ['cramfsck', '-x', destination, self._filename]
        execute_command(args)

# vim: ts=4 sts=4 sw=4 et ai
