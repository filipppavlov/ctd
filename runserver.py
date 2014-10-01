from ctd import app
import argparse

parser = argparse.ArgumentParser('CTD server')
parser.add_argument('--host', default='127.0.0.1', help='Server host address (localhost by default)')
parser.add_argument('--debug', action='store_true', default=False, help='Run server in debug mode (off by default)')

args = parser.parse_args()
app.run(host=args.host, debug=args.debug)