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

import unittest
from .watch import Watch
from .test_utils import FakeException
from .test_utils import FakeClass


class WatchTests(unittest.TestCase):

    def test_watch_with_decode(self):
        fake_resp = FakeClass(self)
        fake_resp.add_method('read_chunked')
        fake_resp.add_method('close')
        fake_resp.add_method('release_conn')
        fake_resp.expect_read_chunked([
            '{"type": "ADDED", "object": {"metadata": {"name": "test1"},"spec": {}, "status": {}}}\n',
            '{"type": "ADDED", "object": {"metadata": {"name": "test2"},"spec": {}, "sta',
            'tus": {}}}\n'
            '{"type": "ADDED", "object": {"metadata": {"name": "test3"},"spec": {}, "status": {}}}\n',
            'should_not_happened\n'],
            decode_content=False)
        fake_resp.expect_close(None)
        fake_resp.expect_release_conn(None)

        fake_api = FakeClass(self)
        fake_api.add_method('get_namespaces', ':return: V1NamespaceList')
        fake_api.expect_get_namespaces(fake_resp, _preload_content=False, watch=True)

        w = Watch()
        count = 1
        for e in w.stream(fake_api.get_namespaces):
            self.assertEqual("ADDED", e['type'])
            # make sure decoder worked and we got a model with the right name
            self.assertEqual("test%d" % count, e['object'].metadata.name)
            count += 1
            # make sure we can stop the watch and the last event with won't be returned
            if count == 4:
                w.stop()

        fake_resp.done()
        fake_api.done()

    def test_watch_with_int_object(self):
        fake_resp = FakeClass(self)
        fake_resp.add_method('read_chunked')
        fake_resp.add_method('close')
        fake_resp.add_method('release_conn')
        fake_resp.expect_read_chunked(['{"type": "ADDED", "object": 1}\n',
                                       '{"type": "ADDED", "object": 2}\n',
                                       '{"type": "ADDED", "object": 3}\n'],
                                      decode_content=False)
        fake_resp.expect_close(None)
        fake_resp.expect_release_conn(None)

        fake_api = FakeClass(self)
        fake_api.add_method('get_num')
        fake_api.expect_get_num(fake_resp, _preload_content=False, watch=True)

        w = Watch(return_type='int')
        count = 1
        for e in w.stream(fake_api.get_num):
            self.assertEqual("ADDED", e['type'])
            self.assertEqual(count, e['object'])
            self.assertEqual(count, e['raw_object'])
            count += 1
        fake_resp.done()
        fake_api.done()

    def test_watch_with_no_return_type(self):
        fake_resp = FakeClass(self)
        fake_resp.add_method('read_chunked')
        fake_resp.add_method('close')
        fake_resp.add_method('release_conn')
        fake_resp.expect_read_chunked(['{"type": "ADDED", "object": "test1"}\n',
                                       '{"type": "ADDED", "object": ["test2"]}\n',
                                       '{"type": "ADDED", "object": 2}\n',
                                       '{"type": "ADDED", "object": 3.5}\n'],
                                      decode_content=False)
        fake_resp.expect_close(None)
        fake_resp.expect_release_conn(None)

        fake_api = FakeClass(self)
        fake_api.add_method('get_thing')
        fake_api.expect_get_thing(fake_resp, _preload_content=False, watch=True)

        w = Watch()
        expect_list = ["test1", ["test2"], 2, 3.5]
        count = 0
        for e in w.stream(fake_api.get_thing):
            self.assertEqual("ADDED", e['type'])
            self.assertEqual(expect_list[count], e['object'])
            self.assertEqual(expect_list[count], e['raw_object'])
            count += 1
        fake_resp.done()
        fake_api.done()

    def test_watch_with_exception(self):
        fake_resp = FakeClass(self)
        fake_resp.add_method('read_chunked')
        fake_resp.add_method('close')
        fake_resp.add_method('release_conn')
        fake_resp.expect_read_chunked(FakeException("expected"), decode_content=False)
        fake_resp.expect_close(None)
        fake_resp.expect_release_conn(None)

        fake_api = FakeClass(self)
        fake_api.add_method('get_namespaces', ':return: V1NamespaceList')
        fake_api.expect_get_namespaces(fake_resp, _preload_content=False, watch=True)

        w = Watch()
        try:
            for e in w.stream(fake_api.get_namespaces):
                pass
        except FakeException:
            pass
            # expected
        fake_resp.done()
        fake_api.done()


if __name__ == '__main__':
    unittest.main()

