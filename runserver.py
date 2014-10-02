import argparse
import logging
from logging.handlers import SMTPHandler

from ctd import app

parser = argparse.ArgumentParser('CTD server')
parser.add_argument('--host', default='127.0.0.1', help='Server host address (localhost by default)')
parser.add_argument('--debug', action='store_true', default=False, help='Run server in debug mode (off by default)')
parser.add_argument('--log', action='store_true', default=False, help='Log errors from the server')
parser.add_argument('--logserver', default='localhost', help='SMTP server for logging errors')
parser.add_argument('--logto', default='', help='E-mail address to send errors to')
parser.add_argument('--logfrom', default='ctd@ctd.com', help='E-mail address to send errors from')

args = parser.parse_args()
if args.log:
    mail_handler = SMTPHandler(args.logserver, args.logfrom, args.logto, 'CTD server failed')
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)
app.run(host=args.host, debug=args.debug)