# Kubernetes Python Client

Python clients for talking to a [kubernetes](http://kubernetes.io/) cluster.

## Example

```python
from __future__ import absolute_import

import k8sutil
import k8sclient
import os

# Configs can be set in Configuration class directly or using helper utility
k8sutil.load_kube_config(os.environ["HOME"] + '/.kube/config')

# Prior to python 3.4 hosts with ip-addresses cannot be verified for SSL. this
# utility function fixes that.
k8sutil.fix_ssl_hosts_with_ipaddress()

v1=k8sclient.CoreV1Api()
print "Listing pods with their IPs:"
ret = v1.list_core_v1_pod_for_all_namespaces(watch=False)
for i in ret.items:
  print "%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name)
```

More examples can be found in [examples](examples/) folder. To run examples, run this command:

```shell
python -m examples.example1
```

(replace example1 with the example base filename)

# Generated client README

for generated client documentation, refer to [generated README](GEN_README.md).

