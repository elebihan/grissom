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
Fossology helpers
"""

import os
import re
import json
import platform
import urllib.request
from http.cookiejar import CookieJar
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from gettext import gettext as _
from datetime import datetime
from collections import namedtuple
from ..common import is_compressed_archive, encode_multipart_formdata


FossologyResult = namedtuple('FossologyResult',
                             ['name', 'upid', 'itemid', 'folder'])

def create_agent(server, secured, user, password):
    """Create agent to interact with Fossology server.

    This function can be used with the 'with' statement::

      with create_agent('fossology.acme.com,' True, 'elmer', 'fudd') as a::
          results = a.query('foo-1.0.0.tar.gz')

    In this case, login will automatically be performed, as well as logout.

    :param address: address of the server.
    :type address: str

    :param secured: if true, use HTTPS instead of HTTP.
    :type secured: bool.

    :param user: name to use for connection.
    :type user: str

    :param password: password for the connection
    :type password: str

    :returns: the agent.
    :rtype: :class:`grissom.legal.fossology.FossologyAgent`
    """
    return FossologyAgent(server, secured, user, password)

class FossologyError(Exception):
    """Error raised when on operation involving Fossology server fails"""

class FossologyAgent(object):
    """Interact with a Fossology server.

    :param address: address of the server.
    :type address: str

    :param secured: if true, use HTTPS instead of HTTP.
    :type secured: bool.

    :param user: name to use for connection.
    :type user: str

    :param password: password for the connection
    :type password: str
    """
    def __init__(self, address, secured=False, user=None, password=None):
        self._user = user
        self._password = password
        self._opener = None
        if secured:
            fmt = "https://{O}/"
        else:
            fmt = "http://{0}/"
        self._url = fmt.format(address)

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, type, value, traceback):
        self.logout()

    def login(self):
        """Log into Fossology."""
        cookie_p = urllib.request.HTTPCookieProcessor(CookieJar())
        self._opener = urllib.request.build_opener(cookie_p)
        self._opener.addheaders = [
            ('User-Agent', "Grissom/1.0 ({0})".format(platform.system())),
            ('Accept', '*/*')
        ]
        data = urlencode({'username': self._user, 'password': self._password})
        data = data.encode('utf-8')
        url = self._url + '?mod=auth'
        self._opener.open(url, data)

    def logout(self):
        """Log out of Fossology."""
        url = self._url + '?mod=auth'
        self._opener.open(url)

    def _check_session(self):
        if not self._opener:
            raise FossologyError(_("No session"))

    def search(self, pattern):
        """Search for uploaded packages.

        The '%' character can be used as a wilcard in the pattern::

          agent.search('foo%.tar.gz')

        :param pattern: pattern for package name.
        :type pattern: str

        :returns: list of matching packages
        :rtype: list of :class:`grissom.legal.fossology.FossologyResult`.
        """
        self._check_session()
        data = urlencode({'searchtype': 'directory', 'filename': pattern})
        data = data.encode('utf-8')
        url = self._url + '?mod=search'
        response = self._opener.open(url, data)
        has_next = True
        results = []
        expr = re.compile(r'^/\?mod=search&searchtype=directory&filename=(.+)&page=(\d+)$')
        while has_next:
            doc = BeautifulSoup(response.read().decode('utf-8'))
            results += self._parse_search_result_doc(doc)
            pages = []
            for anchor in doc.find_all('a'):
                if anchor.string == '[Next]':
                    match = expr.search(anchor['href'])
                    if match:
                        pages.append(anchor['href'])
            if len(pages) >= 2:
                url = self._url.rstrip('/') + pages[-1]
                response = self._opener.open(url)
            else:
                has_next = False
        return results

    def _parse_search_result_doc(self, doc):
        expr = re.compile(r'^/\?mod=browse&upload=(\d+)&item=(\d+)$')
        results = []
        for div in doc.find_all('div'):
            if not div.has_attr('style'):
                continue
            anchors = div.find_all('a')
            if not anchors:
                raise FossologyError(_("Invalid reply"))
            f_crumbs = []
            p_crumbs = []
            for a in anchors[:-1]:
                text = ''.join([s for s in a.stripped_strings])
                if "folder=" in a['href']:
                    f_crumbs.append(text)
                else:
                    p_crumbs.append(text)
            folder = '/'.join(f_crumbs)
            parent = '/'.join(p_crumbs)
            if anchors[-1].has_attr('href'):
                match = expr.match(anchors[-1]['href'])
                if match:
                    children = anchors[-1].contents
                    name = children[-1].string
                    upid = int(match.group(1))
                    itemid = int(match.group(2))
                    if not parent:
                        result = FossologyResult(name,
                                                 upid,
                                                 itemid,
                                                 folder)
                        results.append(result)
        return results

    def _analyse_file(self, filename, as_spdx):
        """Post file for analysis.

        :param filename: path to the file to analyse.
        :type filename: str

        :param as_spdx: if true, output result in SPDX format.
        :type as_spdx: bool

        :returns: the result of the analysis
        :rtype: str
        """

        #
        # NOTE: Fossology does not provide a *real* WEB API. It only supports
        # data posted using wget like this:
        #
        # wget -q -O - --post-file foo.c \
        #   'http://fossology.acme.com/?mod=agent_nomos_once'
        #
        # Internally if read the data posted from 'php://input' which does
        # handle 'multipart/form-data'. So we send the data as it is...
        #

        self._check_session()

        url = self._url
        if as_spdx:
            url += "?mod=spdx_license_once&noCopyright=false&jsonOutput=true"
        else:
            url += "?mod=agent_nomos_once"

        with open(filename, 'rb') as f:
            body = f.read()
            response = self._opener.open(url, body)
            contents = response.read().decode('utf-8').strip()
            return contents

    def analyze_and_format(self, filename):
        """Perform a one-shot analysis of a file and format as SPDX.

        :param filename: path to the file to analyze.
        :type filename: str

        :returns: list of legal information about files.
        :rtype: list
        """
        if not is_compressed_archive(filename):
            raise FossologyError(_("SPDX only works with archives"))

        reply = self._analyse_file(filename, True)
        data = json.loads(reply)
        return data['file_level_info']

    def analyze(self, filename):
        """Perform a one-shot analysis of a file.

        :param filename: path to the file to analyse.
        :type filename: str

        :returns: legal information.
        :rtype: a mapping between strings.
        """
        if is_compressed_archive(filename):
            raise FossologyError(_("Archives not supported"))

        reply = self._analyse_file(filename, False)
        # Handle Fossology <= 2.0.0
        info = reply.split(',')
        if len(info) == 2:
            return {'Copyright': info[0], 'License': info[1]}
        else:
            return {'License': info[0]}

    def query(self, pkgname):
        """Query licenses of the files in a package.

        :param pkgname: name of the package.
        :type pkgname: str

        :returns: list of licenses.
        :rtype: list of str
        """
        self._check_session()
        packages = self.search(pkgname)
        if not packages:
            raise FossologyError(_("Can not find '{0}'").format(pkgname))
        url = "?mod=nomoslicense&upload={0}&item={1}&show=detail"
        url = url.format(packages[0].upid, packages[0].itemid)
        response = self._opener.open(self._url + url)
        doc = BeautifulSoup(response.read().decode('utf-8'))
        results = []
        tables = doc.find_all('table', id='lichistogram')
        if not tables:
            raise FossologyError(_("Invalid reply"))
        for row in tables[0].find_all('tr'):
            cols = row.find_all('td')
            if len(cols) == 3:
                results.append((cols[2].string.strip(), int(cols[0].string)))
        return sorted(results, key=lambda r: r[1], reverse=True)

    def query_all(self, pkgname):
        """Query licenses of the files in a package.

        :param pkgname: name of the package.
        :type pkgname: str

        :returns: list of (filename, license) pairs.
        :rtype: list of (str, str)
        """
        self._check_session()
        packages = self.search(pkgname)
        if not packages:
            raise FossologyError(_("Can not find '{0}'").format(pkgname))
        url = "?mod=license-list&show=detail&upload={0}&item={1}"
        url = url.format(packages[0].upid, packages[0].itemid)
        response = self._opener.open(self._url + url)
        doc = BeautifulSoup(response.read().decode('utf-8'))
        expr = re.compile(r'^{0}/(.+):(.+)'.format(pkgname))
        results = []
        if '.tar.' in pkgname:
            depth = 1
        else:
            depth = 0
        for s in doc.strings:
            match = expr.match(s)
            if match:
                fields = match.group(1).split('/', depth)
                lic = match.group(2)
                results.append((fields[-1], lic))
        return results

    def query_major(self, pkgname):
        """Query major license of a package.

        :param pkgname: name of the package.
        :type pkgname: str

        :returns: the major license
        :rtype: str
        """
        exceptions = [
            'No_license_found', 'Same-license-as',
            'FSF', 'Trademark-ref', 'GPL-exception'
        ]
        major = None
        limit = 0
        for license, count in self.query(pkgname):
            if not license in exceptions:
                if count > limit:
                    major = license
                    limit = count
        return major

    def submit(self, filename):
        """Submit a file to Fossology for analysis.

        :param filename: path to the file to submit.
        :type filename: str.

        :returns: the submission identifier.
        :rtype: int
        """
        url = self._url + '?mod=upload_file'
        with open(filename, 'rb') as f:
            variables = [
                ('folder', '1'),
                ('description', ''),
                ('name', ''),
                ('Check_agent_copyright', '1'),
                ('Check_agent_mimetype', '1'),
                ('Check_agent_nomos', '1'),
                ('Check_agent_pkgagent', '0'),
            ]
            files = [('getfile', os.path.basename(filename), f.read())]
            ct, data = encode_multipart_formdata(variables, files)
            request = urllib.request.Request(url, data)
            request.add_unredirected_header('Content-Type', ct)
            request.add_unredirected_header('Content-Length', len(data))
            response = self._opener.open(request)
            doc = BeautifulSoup(response.read().decode('utf-8'))
            expr = re.compile(r'^/\?mod=showjobs&upload=(\d+)')
            for tag in doc.find_all('a'):
                if tag.has_attr('href'):
                    match = expr.match(tag['href'])
                    if match:
                        return int(match.group(1))
            raise FossologyError(_('Upload failed'))

    def generate_spdx(self, pkgname, author=None, comment=None):
        """Generate SPDX file for a package.

        :param pkgname: name of the package.
        :type pkgname: str.

        :param author: name of the author.
        :type author: str.

        :param comment: a comment to add in the file or None to ignore.
        :type comment: str.

        :returns: the contents of the SPDX file.
        :rtype: str.
        """
        results = self.search(pkgname)
        if not results:
            raise FossologyError(_('Package not found'))
        url = self._url + '?mod=spdx_main_page_confirm'
        params = {
            'spdxVersion': 'SPDX-1.1',
            'create_Date': datetime.now().strftime('%Y-%m-%d'),
            'create_Time': datetime.now().strftime('%H:%M:%S'),
            'creator': author or '',
            'creatorComment': '',
            'documentComment': comment or '',
            'packages': results[0].itemid,
        }

        data = urlencode(params).encode('utf-8')
        response = self._opener.open(url, data)
        contents = response.read().decode('utf-8')
        fmttype = 'tag' # Maybe 'rdf' one day?
        expr = r'window.location.href=\'spdx-output-module/spdx_main_output_{0}.php\?fileSuffix=(.+)\';'
        match = re.search(expr.format(fmttype), contents)
        if not match:
            raise FossologyError(_('Can not create SPDX file'))
        url = 'spdx-output-module/spdx_main_output_{0}.php?fileSuffix={1}'
        url = self._url + url.format(fmttype, match.group(1))
        response = self._opener.open(url)
        return response.read().decode('utf-8')

# vim: ts=4 sts=4 sw=4 et ai
