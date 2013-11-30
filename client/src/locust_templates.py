from locust import Locust, TaskSet, task
from core import StringGenerator
from memcached_dao import MemcachedDao


class KVAccessTasks(TaskSet):
    def on_start(self):
        self.dao = MemcachedDao()
        self.generator = StringGenerator()

    @task
    def read_task(self):
        key = self.generator.gen_key()
        value = self.dao.get(key)
        print "read {} : {}".format(key, value)

    @task
    def write_task(self):
        key = self.generator.gen_key()
        value = self.generator.gen_value()
        self.dao.set(key, value)
        print "write {} : {}".format(key, value)



class WorkloadClient(Locust):
    task_set = KVAccessTasks
    min_wait = 1000
    max_wait = 5000

    def __init__(self):
        super(Locust, self).__init__()
        print "Locust MADDE"
