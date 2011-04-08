#!/usr/bin/env python
import datetime
import re
from glob import glob

import os, sys
if os.path.abspath(os.curdir) not in sys.path:
    sys.path.insert(0, os.path.abspath(os.curdir))

__version__ = '1.0'

def main(locations, patterns):
    def _filter(filename):
        if filename.endswith('.done') and not filename.endswith('.py'):
            return False

        if not (re.findall('^\d+', os.path.basename(filename)) or \
                re.findall(r'^always\b', os.path.basename(filename))):
            raise Exception(os.path.basename(filename))
            return False
        if os.path.isfile(filename + '.done'):
            return False
        return True
    def _repr(filename):
        if os.path.basename(filename).startswith('always'):
            return (999, filename) # so it's run last
        return (int(re.findall('^(\d+)', os.path.basename(filename))[0]),
                filename)
    filenames = []
    for location in locations:
        for pattern in patterns:
            filenames.extend([_repr(x) for x in glob(os.path.join(location, pattern))
                              if _filter(x)])
    filenames.sort()
    for __, filename in filenames:
        sys.path.insert(0, os.path.abspath('.'))
        execfile(filename)
        t = datetime.datetime.now()
        t = t.strftime('%Y/%m/%d %H:%M:%S')
        if not os.path.basename(filename).startswith('always'):
            done_filename = filename + '.done'
            open(done_filename, 'w').write("%s\n" % t)
            print done_filename

from settings import APPS
locations = [os.path.join('apps', x, 'migrations')
             for x in APPS
             if os.path.isdir(os.path.join('apps', x, 'migrations'))]

def run(*args):
    if not args:
        patterns = ['*.py']
    else:
        patterns = args
    main(locations, patterns)
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(run(*sys.argv[1:]))