import threading


class QueueIsEmpty(RuntimeError):
    pass


class ComparisonQueue(object):
    def __init__(self):
        self.queue = []
        self.locked_classes = set()
        self.mutex = threading.Lock()
        self.not_empty = threading.Condition(self.mutex)
        self.all_tasks_done = threading.Condition(self.mutex)

    def put(self, equivalence_class, *args):
        self.mutex.acquire()
        try:
            self.queue.append((equivalence_class, args))
            self.not_empty.notify()
        finally:
            self.mutex.release()

    def get(self, get_callback=None):
        self.not_empty.acquire()
        try:
            while True:
                try:
                    item = self._get()
                    if get_callback is None:
                        return item[1]
                    try:
                        self.not_empty.release()
                        return get_callback(*item[1])
                    finally:
                        self.done_processing(item[0])
                        self.not_empty.acquire()
                except QueueIsEmpty:
                    self.not_empty.wait()
        finally:
            self.not_empty.release()

    def done_processing(self, equivalence_class):
        self.all_tasks_done.acquire()
        try:
            self.locked_classes.remove(equivalence_class)
            if len(self.queue) == 0 or len(self.locked_classes) == 0:
                self.all_tasks_done.notify_all()
        finally:
            self.all_tasks_done.release()

    def join(self):
        self.all_tasks_done.acquire()
        try:
            while len(self.queue) > 0 or len(self.locked_classes) > 0:
                self.all_tasks_done.wait()
        finally:
            self.all_tasks_done.release()

    def _get(self):
        for i in range(len(self.queue)):
            if self.queue[i][0] not in self.locked_classes:
                self.locked_classes.add(self.queue[i][0])
                result = self.queue[i]
                del self.queue[i]
                return result
        raise QueueIsEmpty()