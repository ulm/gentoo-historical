#!/usr/bin/python -O


try:
    import psycho
    psycho.full()
except ImportError:
    pass

import os
from scgi.quixote_handler import QuixoteHandler, main
from quixote.publish import Publisher
from quixote import config
import quixote.http_request
import quixote.http_response
quixote.http_request.DEFAULT_CHARSET = 'utf-8'
quixote.http_response.DEFAULT_CHARSET = 'utf-8'


from quixote import enable_ptl
enable_ptl()

CURDIR = os.path.dirname(__file__)

# The following is as specified in the Quixote docs and
# http://tinyurl.com/78p3b
class MyAppHandler(QuixoteHandler):
    publisher_class = Publisher
    root_namespace = "packages"
    prefix = ""

    def __init__(self, *args, **kwargs):
        QuixoteHandler.__init__(self, *args, **kwargs)
        conf = config.Config()
        conf.read_file('%s/packages.conf' % CURDIR)
        self.publisher.set_config(conf)
        self.publisher.setup_logs()


if __name__ == '__main__':
    main(MyAppHandler)
