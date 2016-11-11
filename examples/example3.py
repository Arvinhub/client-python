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

import k8sutil
import k8sclient
import os
import sys

# Configs can be set in Configuration class directly or using helper utility
k8sutil.load_kube_config(os.environ["HOME"] + '/.kube/config')

k8sclient.configuration.debug = True

# Prior to python 3.4 hosts with ip-addresses cannot be verified for SSL. this
# utility function fixes that.
k8sutil.fix_ssl_hosts_with_ipaddress()

v1=k8sclient.CoreV1Api()
print "Listening on namespace changes::"
k8sclient.configuration.preload_content = False
ret = v1.list_core_v1_namespace(watch=True)

line = ""
while ret.readable():
    data = ret.read(1)
    if not data:
        break
    if data == '\r' or data == '\n':
        if not line:
            continue
        print "Line: " + line
        line = ""
    else:
        line += data
print "Ended."
