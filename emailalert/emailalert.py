import smtplib
from email.mime.text import MIMEText
import threading
import time
import os

BODY = """
Image series became unstable:
%s
"""
FROM = 'godknows@imagediff.com'


def send_email(form_email, to_email, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = form_email
    msg['To'] = to_email

    s = smtplib.SMTP('localhost')
    s.sendmail(form_email, [to_email], msg.as_string())
    s.quit()


class EmailRecord(object):
    def __init__(self, series):
        self.series = series
        self.new = series.get_latest_object()
        if series.ideal is not None:
            self.comperand = series.get_ideal()
            self.ideal = True
        elif len(series.records) > 1:
            self.comperand = series.get_object(len(series.records) - 2)
            self.ideal = False


class EmailAlert(object):
    def __init__(self, db_path, from_email, subject, render_body, send_period):
        self.emails = {}
        self.pending_emails = {}
        self.from_email = from_email
        self.render_body = render_body
        self.db_path = db_path
        self.send_period = send_period
        self.subject = subject
        self._read_emails(db_path)
        self.mutex = threading.Lock()
        if self.send_period > 0:
            threading.Thread(target=self._send_loop)

    def _read_emails(self, db_path):
        if os.path.exists(db_path):
            with open(db_path, 'rt') as f:
                for line in f:
                    email, path = line.split(' ')
                    path = path.strip()
                    self.emails.setdefault(path, set()).add(email)

    def add_email(self, email, path):
        self.emails.setdefault(path, set()).add(email)
        with open(self.db_path, 'at') as f:
            f.write('%s %s\n' % (email, path))

    def alert(self, series):
        for each in self.emails:
            if series.path.startswith(each):
                for i in self.emails[each]:
                    with self.mutex:
                        record = EmailRecord(series)
                        self.pending_emails.setdefault(i, set()).add(record)
        if self.send_period == 0:
            self._process()

    def remove_email(self, email, path):
        self.emails[path].remove(email)
        with open(self.db_path, 'wt') as f:
            for each in self.emails:
                for i in self.emails[each]:
                    f.write('%s %s\n' % (i, each))

    def get_emails(self, path):
        result = []
        for each in self.emails:
            if path.startswith(each):
                for i in self.emails[each]:
                    result.append((i, each))
        return result

    def _process(self):
        with self.mutex:
            for each in self.pending_emails:
                send_email(self.from_email, each, self.subject, self.render_body(each, self.pending_emails[each]))
                print each
            self.pending_emails.clear()

    def _send_loop(self):
        time.sleep(self.send_period * 60)
        self._process()