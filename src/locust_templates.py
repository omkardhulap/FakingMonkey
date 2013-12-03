
from locust import Locust, TaskSet, task

import config
from core import StringGenerator
from memcached_dao import MemcachedDao


class KVAccessTasks(TaskSet):
    def on_start(self):
        self.dao = MemcachedDao()
        self.generator = StringGenerator()

    @task(int(config.rw_ratio * 1000))
    def read_task(self):
        key = self.generator.gen_key()
        value = self.dao.get(key)

    @task(int((1.0 - config.rw_ratio) * 1000))
    def write_task(self):
        key = self.generator.gen_key()
        value = self.generator.gen_value()
        self.dao.set(key, value)



class WorkloadClient(Locust):
    task_set = KVAccessTasks
    min_wait = 1000
    max_wait = 1000

    def __init__(self):
        super(Locust, self).__init__()
