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

import k8sclient
import json

import pydoc


class SimpleNamespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def _find_return_type(func):
    for line in pydoc.getdoc(func).splitlines():
        if line.startswith(":return:"):
            return line[len(":return:"):].strip()
    return ""


class Watch(object):

    def __init__(self, return_type=None):
        self._return_type = return_type
        self._stop = False

    def stop(self):
        self._stop = True

    def stream(self, func, *args, **kwargs):
        """Watch an API resource and stream the result back as a generators.

        :param func: The API function pointer. Any parameter to the function can be passed after this parameter.

        :return: Event object with these keys:
                   'type': The type of event such as "ADDED", "DELETED", etc.
                   'raw_object': a dict representing the watched object.
                   'object': A model representation of raw_object. The name of model will be determined based on
                             the func's doc string. If it cannot be determined, 'object' value will be the same
                             as 'raw_object'.

        Example:
            v1 = k8sclient.CoreV1Api()
            watch = k8sutil.Watch()
            for e in watch.stream(v1.list_namespace, resource_version=1127):
                type = e['type']
                object = e['object']  # object is one of type return_type
                raw_object = e['raw_object']  # raw_object is a dict
                ...
                if should_stop:
                    watch.stop()
        """

        if self._return_type:
            return_type = self._return_type
        else:
            return_type = _find_return_type(func)
            # Hacky assumption that watching `func` return TypeList in non-watch mode and an event with
            # object of type in Type in watch mode.
            if return_type.endswith("List"):
                return_type = return_type[:len(return_type)-4]

        api_client = k8sclient.ApiClient()
        kwargs['watch'] = True
        kwargs['_preload_content'] = False
        resp = func(*args, **kwargs)
        try:
            prev = ""
            for seg in resp.read_chunked(decode_content=False):
                if isinstance(seg, bytes):
                    seg = seg.decode('utf8')
                seg = prev + seg
                lines = seg.split("\n")
                if not seg.endswith("\n"):
                    prev = lines[-1]
                    lines = lines[:-1]
                else:
                    prev = ""
                for l in lines:
                    if l:
                        j = json.loads(l)
                        j['raw_object'] = j['object']
                        if return_type:
                            obj = SimpleNamespace(data=json.dumps(j['raw_object']))
                            j['object'] = api_client.deserialize(obj, return_type)
                        yield j
                        if self._stop:
                            break
                if self._stop:
                    break
        finally:
            resp.close()
            resp.release_conn()


