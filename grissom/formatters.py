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
Helper classes for formatting data
"""

import abc
from grissom.common import topological_sort

def _find_arcs_for(node, graph):
    for n, arcs in graph:
        if node == n:
            return arcs
    return []

def _find_unreachable_nodes(graph):
    nodes = []
    for node, arcs in graph:
        nodes += arcs
    return [(n, a) for n, a in graph if n not in nodes]

class GraphFormatter(object):
    """Abstract Base Class for formatting a graph"""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def format(self, graph):
        """Format a graph.

        :param graph: graph to be formatted.
        """
        return

class GraphSimpleFormatter(GraphFormatter):
    """Format an acyclic directed graph.

    The acyclic directed graph represented as an adjacent list.

    [(1, [2, 3]), (3, [4, 5])]
    """

    def format(self, graph):
        for node, arcs in reversed(topological_sort(dict(graph))):
            if arcs:
                print("{0:<24}: {1}".format(node, ', '.join(arcs)))

class GraphPrettyFormatter(GraphFormatter):
    """Format an acyclic directed graph in a pretty way."""

    def format(self, graph):
        for node, arcs in _find_unreachable_nodes(graph):
            segs = []
            self._print_node(segs, False, node, arcs, graph)

    def _print_node(self, segs, last, node, arcs, graph):
        if not segs:
            prefix = '* '
        else:
            prefix = ''
        print("{0}{1}{2}".format(prefix, ''.join(segs), node))

        if len(segs) == 0:
            segs.append('  ')
        elif len(segs) >= 2:
            segs.pop()
            segs.pop()
            if last:
                segs.append(' ')
            else:
                segs.append('│')
            segs.append('   ')

        for arc in arcs:
            if arc == arcs[-1]:
                last = True
            else:
                last = False

            if last:
                segs.append('└')
            else:
                segs.append('├')
            segs.append('── ')
            new_arcs = _find_arcs_for(arc, graph)
            self._print_node(segs, last, arc, new_arcs, graph)
            segs.pop()
            segs.pop()

_GRAPH_DOT_FMT_MAX_NODES = 6

class GraphDotFormatter(GraphFormatter):
    """Format an acyclic directed graph in DOT file format.

    Process the ouput with Graphviz to get a pretty diagram.
    """

    def format(self, graph):
        print("digraph G\n{")
        if len(graph) >= _GRAPH_DOT_FMT_MAX_NODES:
            print("rankdir=LR")
        for node, arcs in reversed(topological_sort(dict(graph))):
            if arcs:
                for arc in arcs:
                    print("\t\"{0}\" -> \"{1}\";".format(node, arc))
        print("}")

class SpdxFormatter(object):
    """Abstract Base Class for formatting SPDX data"""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def format(self, filename, spdx_info):
        """Format SPDX for a package.

        :param filename: package filename.
        :type filename: str.

        :param spdx_info: SPDX information.
        :type spdx: a list of mappings between strings.
        """
        return

class SpdxTagValueFormatter(SpdxFormatter):
    """Format SPDX data as tag/value."""

    _SPDX_FIELDS = (
        'FileName',
        'FileType',
        'FileChecksum',
        'LicenseConcluded',
        'LicenseInfoInFile'
    )

    def format(self, filename, spdx_info):
        text = "PackageFileName: {0}\n".format(filename)
        for element in spdx_info:
            for f in self._SPDX_FIELDS:
                text += "\n{0}: {1}".format(f, element[f])
            text += '\n'
        print(text)

__graph_formatters = {
    'simple': GraphSimpleFormatter,
    'pretty': GraphPrettyFormatter,
    'dot': GraphDotFormatter,
}

def create_graph_formatter(name):
    """Create a formatter from name.

    :param name: name of the formatter.
    :type name: str

    :returns: the formatter
    :rtype: :class:`grissom.formatters.GraphFormatter`
    """
    klass = __graph_formatters[name]
    return klass()

# vim: ts=4 sts=4 sw=4 et ai
