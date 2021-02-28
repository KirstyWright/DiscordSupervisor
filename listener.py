#!/usr/bin/python

import sys
from storage import Storage
from supervisor.childutils import listener

def main(args):
    # logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format='%(asctime)s %(levelname)s %(filename)s: %(message)s')
    # logger = logging.getLogger("supervisord-eventlistener")

    storage = Storage()
    while True:
        headers, body = listener.wait(sys.stdin, sys.stdout)
        body = dict([pair.split(":") for pair in body.split(" ")])

        try:
            storage.query("INSERT INTO messages (process_name, content) VALUES (?, ?)", [
                body["processname"], headers["eventname"]])
        except Exception as e:
            # logger.critical("Unexpected Exception: %s", str(e))
            listener.fail(sys.stdout)
            exit(1)
        else:
            listener.ok(sys.stdout)

if __name__ == '__main__':
    main(sys.argv[1:])
