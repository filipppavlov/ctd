import unittest
import threading
import time
from comparisons.queue import ComparisonQueue


class TestQueue(unittest.TestCase):
    def test_can_join_empty_queue(self):
        q = ComparisonQueue()
        q.join()
        self.assertTrue(True)

    def test_can_get_item_that_was_put_into_queue(self):
        q = ComparisonQueue()
        q.put('abc', 123)
        q.get(lambda x: self.assertEqual(x, 123))

    def test_items_stored_in_fifo_order(self):
        q = ComparisonQueue()
        q.put('abc', 123, 456)
        q.put('def', 234)
        q.get(lambda x, y: self.assertEqual(x, 123) and self.assertEqual(y, 456))
        q.get(lambda x: self.assertEqual(x, 234))

    def test_can_join_queue_after_processing(self):
        q = ComparisonQueue()
        q.put('abc', 123)
        q.get(lambda x: self.assertEqual(x, 123))
        q.join()
        self.assertTrue(True)

    def test_can_get_item_without_callback(self):
        q = ComparisonQueue()
        q.put('abc', 123)
        self.assertEqual(q.get(), (123, ))

    def test_can_get_item_without_callback_and_finish_processing(self):
        q = ComparisonQueue()
        q.put('abc', 123, 456)
        self.assertEqual(q.get(), (123, 456))
        q.done_processing('abc')
        q.join()
        self.assertTrue(True)

    def test_can_get_items_asynchronously(self):
        q = ComparisonQueue()
        q.put('abc', 123)
        q.put('def', 789)

        processed = []

        def worker():
            def xxx(x):
                processed.append(x)
            while True:
                q.get(xxx)
        t0 = threading.Thread(target=worker)
        t0.daemon = True
        t0.start()
        q.join()
        self.assertItemsEqual(processed, [123, 789])

    def test_same_class_is_processed_synchronously(self):
        q = ComparisonQueue()
        order = []

        def worker():
            def xxx(x):
                order.append(x)
                time.sleep(0.5)
            while True:
                q.get(xxx)

        t0 = threading.Thread(target=worker)
        t0.daemon = True
        t1 = threading.Thread(target=worker)
        t1.daemon = True
        t0.start()
        q.put('abc', 123)
        q.put('abc', 456)
        q.put('def', 789)
        time.sleep(0.1)
        t1.start()

        q.join()
        self.assertEqual(order, [123, 789, 456])


