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

from __future__ import absolute_import

import atexit
import base64
import os
import tempfile
import urllib3
import yaml

import k8sclient.configuration

_tempfiles = []


def _cleanup_tempfiles():
    for f in _tempfiles:
        os.remove(f)


def _create_temp_file_with_content(content):
    if len(_tempfiles) == 0:
        atexit.register(_cleanup_tempfiles)
    _, name = tempfile.mkstemp()
    _tempfiles.append(name)
    fd = open(name, 'w')
    try:
        fd.write(base64.decodestring(content))
    finally:
        fd.close()
    return name


def _find_object_with_name(o, name):
    for c in o:
        if c['name'] == name:
            return c
    return None


def _file_from_file_or_data(o, file_key_name, data_key_name=None):
    if not data_key_name:
        data_key_name = file_key_name + "-data"
    if data_key_name in o:
        return _create_temp_file_with_content(o[data_key_name])
    if file_key_name in o:
        return o[file_key_name]
    return None


def _data_from_file_or_data(o, file_key_name, data_key_name=None):
    if not data_key_name:
        data_key_name = file_key_name + "_data"
    if data_key_name in o:
        return o[data_key_name]
    if file_key_name in o:
        with open(o[file_key_name], 'r') as f:
            data = f.read()
        return data
    return None


def load_kube_config(config_file):
    c = k8sclient.configuration
    f = open(config_file)
    try:
        config = yaml.load(f)
        active_context = _find_object_with_name(config['contexts'], config['current-context'])['context']
        user = _find_object_with_name(config['users'],active_context['user'])['user']
        cluster = _find_object_with_name(config['clusters'],active_context['cluster'])['cluster']
        if 'server' in cluster:
            c.host = cluster['server']
        if 'username' in user and 'password' in user:
            c.api_key['authorization'] = urllib3.util.make_headers(
                basic_auth=user['username'] + ':' + user['password']).get('authorization')
        token = _data_from_file_or_data(user, 'tokenFile', 'token')
        if token:
            c.api_key['authorization'] = "bearer " + token

        c.ssl_ca_cert = _file_from_file_or_data(cluster, 'certificate-authority')
        c.cert_file = _file_from_file_or_data(user, 'client-certificate')
        c.key_file = _file_from_file_or_data(user, 'client-key')
    finally:
        f.close()
