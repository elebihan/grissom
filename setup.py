#!/usr/bin/env python3
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

from distutils.core import setup
from disthelpers import build, build_trans, build_man, install_data
from glob import glob
from grissom import __version__

setup(name='grissom',
      version=__version__,
      description='FOSS compliance tools',
      long_description='''
      Collection of tools to check FOSS compliance of programs.
      ''',
      license='GPLv3',
      url='https://github.com/elebihan/grissom/',
      platforms=['linux'],
      classifiers=('Programming Language :: Python :: 3',
                   'Intended Audience :: Developers',
                   'Natural Language :: English'
                   'License :: OSI Approved :: GNU General Public License (GPL)',),
      keywords=['grissom', 'FOSS', 'compliance'],
      requires=['pyelftools (>=0.21)',
                'filemagic (>=1.6)',
                'beautifulsoup4 (>=4.3.2)',
                'docutils (>=0.11)'],
      packages=['grissom',
                'grissom.binfmt',
                'grissom.extractors',
                'grissom.legal'],
      scripts=glob('scripts/grissom-*'),
      data_files=[('share/man/man1', glob('build/man/man1/grissom*.1')),
                  ('share/man/man5', glob('build/man/man5/grissom*.5')),
                  ('share/man/man7', glob('build/man/man5/grissom*.7')),],
      author='Eric Le Bihan',
      author_email='eric.le.bihan.dev@free.fr',
      cmdclass = {'build': build,
                  'build_man': build_man,
                  'build_trans': build_trans,
                  'install_data': install_data})

# vim: ts=4 sts=4 sw=4 sta et ai
