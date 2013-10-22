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
Binary file data extraction core classes.
"""

class Extractor(object):
    """Base class for extracting data from binary files.

    :param filename: path to the file to inspect.
    :type filename: str
    """
    def __init__(self, filename):
        self._filename = filename
        self._desc = 'Unknown'

    @property
    def description(self):
        return self._desc

    def extract(self, destination):
        """Extract data .

        :param destination: path to destination directory.
        :type destination: str
        """
# vim: ts=4 sts=4 sw=4 et ai
