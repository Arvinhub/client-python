import sys
import os.path
import json
from collections import OrderedDict

_ops = ['get', 'put', 'post', 'delete', 'options', 'head', 'patch']


def _title(str):
    if len(str) == 0:
        return str
    return str[0].upper() + str[1:]


def _to_camel_case(s):
    return ''.join(_title(y) for y in s.split("_"))


def iterate_through_operations(js, fn):
    for k, v in js['paths'].iteritems():
        for o in _ops:
            if o in v:
                fn(v[o])


def process_swagger(infile, outfile):
    with open(infile, 'r') as f:
        j = json.load(f, object_pairs_hook=OrderedDict)

        def strip_tags_from_operation_id(o):
            op_id = o['operationId']
            for t in o['tags']:
                op_id = op_id.replace(_to_camel_case(t), '')
            o['operationId'] = op_id

        iterate_through_operations(j, strip_tags_from_operation_id)

        with open(outfile, 'w') as out:
            json.dump(j, out, sort_keys=False, indent=2, separators=(',', ': '), ensure_ascii=True)


def main():
    if len(sys.argv) < 3:
        print "Usage:\n\tpython %s infile outfile.\n" % sys.argv[0]
        sys.exit(0)
    if not os.path.isfile(sys.argv[1]):
        print "Input file %s does not exist." % sys.argv[1]
    process_swagger(sys.argv[1], sys.argv[2])

main()
