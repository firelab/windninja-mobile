#! /usr/bin/python3
import argparse
import sys
import signal
import datetime

import windninja_server.windninjaqueue.manager as wnmanager
import windninja_server.windninjaconfig as wnconfig


def write_stdout(s):
    sys.stdout.write("[{}]:{}\n".format(datetime.datetime.now().isoformat(), s))
    sys.stdout.flush()


def signal_handler(signal, frame):
    write_stdout("Ctrl+C detected...")
    wnmanager.CANCEL = True


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true", required=False)
    args = parser.parse_args()

    write_stdout("Starting queue manager [verbose={}]...".format(args.verbose))

    write_stdout("Press Ctrl+C to cancel")
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    wnmanager.VERBOSE = args.verbose
    wnmanager.main_loop(wnconfig.Config.QUEUE)

    write_stdout("Exiting queue manager...")
