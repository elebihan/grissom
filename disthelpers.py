# -*- coding: utf-8 -*-
#
# disthelpers.py - useful distutils helper commands
#
# Copyright (c) 2014 Eric Le Bihan <eric.le.bihan.dev@free.fr>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from distutils import cmd
from distutils.command.build import build as _build
from distutils.errors import DistutilsOptionError
from docutils.core import publish_file
import os
import subprocess

class extract_messages(cmd.Command):
    description = 'extract localizable strings from source code'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        domain = self.distribution.get_name()
        potin_file = os.path.join(os.curdir, 'po', 'POTFILES.in')
        pot_file = os.path.join(os.curdir, 'po', domain + '.pot')
        args = [
            'xgettext', '-Lpython', '-k_', '-f', potin_file, '-o', pot_file,
            '--package-name', self.distribution.get_name(),
        ]
        subprocess.check_call(args)

class init_catalog(cmd.Command):
    description = 'create a new catalog based on a POT file'
    user_options = [
        ('locale=', 'l', 'locale for the new localized catalog'),
    ]

    def initialize_options(self):
        self.locale = None

    def finalize_options(self):
        if not self.locale:
            raise DistutilsOptionError('please provide a locale')

    def run(self):
        domain = self.distribution.get_name()
        pot_file = os.path.join(os.curdir, 'po', domain + '.pot')
        po_file = os.path.join(os.curdir, 'po', self.locale + '.po')
        args = [
            'msginit', '--input', pot_file, '--output', po_file,
            '--locale', self.locale,
        ]
        subprocess.check_call(args)

class update_catalog(cmd.Command):
    description = 'update an existing catalog from a POT file'
    user_options = [
        ('locale=', 'l', 'locale of the localized catalog'),
    ]

    def initialize_options(self):
        self.locale = None

    def finalize_options(self):
        if not self.locale:
            raise DistutilsOptionError('please provide a locale')

    def run(self):
        domain = self.distribution.get_name()
        pot_file = os.path.join(os.curdir, 'po', domain + '.pot')
        po_file = os.path.join(os.curdir, 'po', self.locale + '.po')
        args = ['msgmerge', '--update', po_file, pot_file]
        subprocess.check_call(args)

class build_catalog(cmd.Command):
    description = 'compile *.po file into *.mo file'
    user_options = [
        ('locale=', 'l', 'locale of the localized catalog'),
    ]

    def initialize_options(self):
        self.locale = None

    def finalize_options(self):
        pass

    def run(self):
        locales = []
        domain = self.distribution.get_name()
        po_dir = os.path.join(os.path.dirname(os.curdir), 'po')

        if self.locale:
            locales.append(self.locale)
        else:
            for path, names, filenames in os.walk(po_dir):
                for f in filenames:
                    if f.endswith('.po'):
                        locale = f[:-3]
                        locales.append(locale)

        for locale in locales:
            mo_dir = os.path.join('build', 'locale', locale, 'LC_MESSAGES')
            src = os.path.join(po_dir, locale + '.po')
            dst = os.path.join(mo_dir, domain + '.mo')
            if not os.path.exists(mo_dir):
                os.makedirs(mo_dir)
            print("compiling {0}".format(src))
            args = ['msgfmt', src, '--output-file', dst]
            subprocess.check_call(args)
            locale_dir = os.path.join('share', 'locale', locale, 'LC_MESSAGES')
            self.distribution.data_files.append((locale_dir, [dst]))

class build_man(cmd.Command):
    description = 'build MAN page from restructuredtext'

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        src_dir = os.path.join(os.path.dirname(os.curdir), 'man')
        dst_dir = os.path.join('build', 'man')
        for path, names, filenames in os.walk(src_dir):
            for f in filenames:
                if f.endswith('.rst'):
                    filename, section, ext = f.rsplit('.', 2)
                    if not os.path.exists(dst_dir):
                        os.makedirs(dst_dir)
                    src = os.path.join(path, f)
                    dst = os.path.join(dst_dir, filename + '.' + section)
                    print("converting {0}".format(src))
                    publish_file(source_path=src,
                                 destination_path=dst,
                                 writer_name='manpage')
                    man_dir = os.path.join('share', 'man', 'man' + section)
                    self.distribution.data_files.append((man_dir, [dst]))

class build(_build):
    sub_commands = _build.sub_commands
    sub_commands += [('build_catalog', None)] + [('build_man', None)]

    def run(self):
        _build.run(self)

# vim: ts=4 sts=4 sw=4 sta et ai
