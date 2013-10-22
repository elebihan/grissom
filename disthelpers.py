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

from distutils import cmd
from distutils.command.install_data import install_data as _install_data
from distutils.command.build import build as _build
from docutils.core import publish_file
import os
import subprocess

MO_FILE = 'grissom.mo'

class build_trans(cmd.Command):

    description = 'compile *.po files into *.mo files'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        po_dir = os.path.join(os.path.dirname(os.curdir), 'po')
        for path, names, filenames in os.walk(po_dir):
            for f in filenames:
                if f.endswith('.po'):
                    lang = f[:-3]
                    mo_dir = os.path.join('build',
                                          'locale',
                                          lang,
                                          'LC_MESSAGES')
                    src = os.path.join(path, f)
                    dst = os.path.join(mo_dir, MO_FILE)
                    if not os.path.exists(mo_dir):
                        os.makedirs(mo_dir)
                    print("compiling {0}".format(src))
                    args = ['msgfmt', src, '--output-file', dst]
                    subprocess.check_call(args)

class build_man(cmd.Command):
    description = 'build MAN page from restructuredtext'
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        man_dir = os.path.join(os.path.dirname(os.curdir), 'man')
        for path, names, filenames in os.walk(man_dir):
            for f in filenames:
                if f.endswith('.rst'):
                    filename, section, ext = f.rsplit('.', 2)
                    dst_dir = os.path.join('build', 'man', 'man' + section)
                    if not os.path.exists(dst_dir):
                        os.makedirs(dst_dir)
                    src = os.path.join(path, f)
                    dst = os.path.join(dst_dir, filename + '.' + section)
                    print("converting {0}".format(src))
                    publish_file(source_path=src,
                                 destination_path=dst,
                                 writer_name='manpage')

class build(_build):
    sub_commands = _build.sub_commands
    sub_commands += [('build_trans', None)] + [('build_man', None)]
    def run(self):
        _build.run(self)

class install_data(_install_data):
    def run(self):
        locale_dir = os.path.join('build', 'locale')
        for lang in os.listdir(locale_dir):
            lang_dir = os.path.join('share',
                                    'locale',
                                    lang,
                                    'LC_MESSAGES')
            lang_file = os.path.join(locale_dir, lang, 'LC_MESSAGES', MO_FILE)
            self.data_files.append((lang_dir, [lang_file]))
            _install_data.run(self)

# vim: ts=4 sts=4 sw=4 sta et ai
