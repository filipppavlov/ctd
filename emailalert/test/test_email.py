import unittest
import emailalert.emailalert as emailalert
import tempfile
import shutil
import os


class MockedSeries(object):
    def __init__(self, path):
        self.path = path
        self.ideal = None
        self.records = [None]
        self.get_latest_object = lambda: None


def _empty_render_body(*args):
    pass


class TestEmailAlert(unittest.TestCase):
    def setUp(self):
        self.send_email_calls = []

        def mock_send_email(*args):
            self.send_email_calls.append(args)

        emailalert.send_email = mock_send_email
        self.db_path = os.path.join(tempfile.mkdtemp(), 'emails.txt')

    def tearDown(self):
        shutil.rmtree(os.path.dirname(self.db_path))

    def test_can_send_an_alert_for_root_subscriber(self):
        e = emailalert.EmailAlert(self.db_path, 'from@emailalert.com', 'Test subject', _empty_render_body, 0)
        e.add_email('to@emailalert.com', '')
        e.alert(MockedSeries('abc'))

        self.assertEqual(self.send_email_calls, [('from@emailalert.com', 'to@emailalert.com', 'Test subject', None)])

    def test_can_send_an_alert_for_prefix_subscriber(self):
        e = emailalert.EmailAlert(self.db_path, 'from@emailalert.com', 'Test subject', _empty_render_body, 0)
        e.add_email('to@emailalert.com', 'ab')
        e.alert(MockedSeries('abc'))

        self.assertEqual(self.send_email_calls, [('from@emailalert.com', 'to@emailalert.com', 'Test subject', None)])

    def test_does_not_send_alert_if_prefix_does_not_match(self):
        e = emailalert.EmailAlert(self.db_path, 'from@emailalert.com', 'Test subject', _empty_render_body, 0)
        e.add_email('to@emailalert.com', 'ab')
        e.alert(MockedSeries('def'))

        self.assertEqual(self.send_email_calls, [])

    def test_can_send_an_alert_to_different_recipients(self):
        e = emailalert.EmailAlert(self.db_path, 'from@emailalert.com', 'Test subject', _empty_render_body, 0)
        e.add_email('to1@emailalert.com', '')
        e.add_email('to2@emailalert.com', '')
        e.alert(MockedSeries('abc'))

        self.assertItemsEqual(self.send_email_calls, [('from@emailalert.com', 'to1@emailalert.com', 'Test subject',
                                                       None), ('from@emailalert.com', 'to2@emailalert.com',
                                                               'Test subject', None)])

    def test_only_one_email_send_if_multiply_subscribed(self):
        e = emailalert.EmailAlert(self.db_path, 'from@emailalert.com', 'Test subject', _empty_render_body, 0)
        e.add_email('to1@emailalert.com', '')
        e.add_email('to1@emailalert.com', 'a')
        e.alert(MockedSeries('abc'))

        self.assertItemsEqual(self.send_email_calls, [('from@emailalert.com', 'to1@emailalert.com', 'Test subject',
                                                       None)])

    def test_can_get_emails(self):
        e = emailalert.EmailAlert(self.db_path, 'from@emailalert.com', 'Test subject', 'Test body', 0)
        e.add_email('to1@emailalert.com', '')
        e.add_email('to2@emailalert.com', 'a')
        e.add_email('to3@emailalert.com', 'b')
        self.assertItemsEqual(e.get_emails('abc'), (('to1@emailalert.com', ''), ('to2@emailalert.com', 'a')))

    def test_remove_non_existent_email_raises(self):
        e = emailalert.EmailAlert(self.db_path, 'from@emailalert.com', 'Test subject', 'Test body', 0)
        e.add_email('to@emailalert.com', '')
        with self.assertRaises(KeyError):
            e.remove_email('a@emailalert.com', '')

    def test_can_remove_email(self):
        e = emailalert.EmailAlert(self.db_path, 'from@emailalert.com', 'Test subject', 'Test body', 0)
        e.add_email('to1@emailalert.com', 'a')
        e.add_email('to2@emailalert.com', 'a')
        e.remove_email('to1@emailalert.com', 'a')
        self.assertItemsEqual(e.get_emails('abc'), (('to2@emailalert.com', 'a'),))