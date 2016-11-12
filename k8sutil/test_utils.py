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


class FakeException(Exception):
    pass


class FakeClass(object):
    def __init__(self, test_case):
        self._test_case = test_case
        self._methods = []

    def add_method(self, method, doc=None):
        self._methods.append(method)
        setattr(self, "_%s_rets" % method, [])
        setattr(self, method, lambda *args, **kwargs: self._method(getattr(self, "_%s_rets" % method), args, kwargs))
        setattr(self, "expect_%s" % method,
                lambda _expect_ret, *args, **kwargs: getattr(self, "_%s_rets" % method).append({'ret': _expect_ret, 'args': args, 'kwargs': kwargs}))
        setattr(getattr(self, method), '__doc__', doc)

    def _method(self,_fake_rets, args, kwargs):
        self._test_case.assertTrue(len(_fake_rets)>0)
        ret = _fake_rets.pop(0)
        self._test_case.assertEquals(ret['args'], args)
        self._test_case.assertEquals(ret['kwargs'], kwargs)
        if isinstance(ret['ret'], FakeException):
            raise ret['ret']
        return ret['ret']

    def done(self):
        # make sure all methods expected to call, actually called.
        for method in self._methods:
            rets = getattr(self, "_%s_rets" % method)
            self._test_case.assertTrue(len(rets) == 0,
                                       "Expected %d more calls to %s is expected: %s" % (len(rets), method, rets))


