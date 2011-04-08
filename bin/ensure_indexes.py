#!/usr/bin/env python
import os, sys
if os.path.abspath(os.curdir) not in sys.path:
    sys.path.insert(0, os.path.abspath(os.curdir))

import settings
for app_name in settings.APPS:
    _app = __import__('apps.%s' % app_name, globals(), locals(),
          ['indexes'], -1)
    try:
        _app.indexes.run()
        print "Ensured indexes for", _app.indexes
    except AttributeError:
        print "Skipping", repr(_app)
        continue
#from apps.eventlog.indexes import run as eventlog_run
#eventlog_run()