# Copyright 2016 The Kubernetes Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import urllib3
import ipaddress
import sys

prev_match_hostname = None


def _to_unicode(obj):
    if isinstance(obj, str) and sys.version_info < (3,):
        obj = unicode(obj, encoding='ascii', errors='strict')
    return obj


def _ip_address(str):
    return ipaddress.ip_address(_to_unicode(str).rstrip())


def _match_hostname(cert, hostname):
    global prev_match_hostname
    if not prev_match_hostname:
        raise TypeError("prev_match_hostname should not be None")
    try:
        # Divergence from upstream: ipaddress can't handle byte str
        host_ip = _ip_address(hostname)
        san = cert.get('subjectAltName', ())
        for key, value in san:
            if key == 'IP Address':
                if host_ip is not None and _ip_address(value) == host_ip:
                    return
    except ValueError:
        pass
    return prev_match_hostname(cert, hostname)

def fix_ssl_hosts_with_ipaddress():
    """urllib3 match_hostname does not support IP addresses. This function is adding the support."""
    global prev_match_hostname
    if getattr(getattr(urllib3, "connectionpool", None), "match_hostname", None):
        prev_match_hostname=urllib3.connectionpool.match_hostname
        urllib3.connectionpool.match_hostname = _match_hostname
    if getattr(getattr(urllib3, "connection", None), "match_hostname", None):
        prev_match_hostname=urllib3.connection.match_hostname
        urllib3.connection.match_hostname = _match_hostname
