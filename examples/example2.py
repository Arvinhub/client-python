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


def main():
    # Configs can be set in Configuration class directly or using helper utility
    k8sutil.load_kube_config(os.environ["HOME"] + '/.kube/config')

    # Prior to python 3.4 hosts with ip-addresses cannot be verified for SSL. this
    # utility function fixes that.
    k8sutil.fix_ssl_hosts_with_ipaddress()

    v1 = k8sclient.CoreV1Api()
    count = 10
    watch = k8sutil.Watch()
    for x in watch.stream(v1.list_namespace):
        print("Event: %s" % str(x))
        print("Type of rest object: %s" % type(x['object']))
        count -= 1
        if not count:
            watch.stop()

    print("Ended.")


main()
