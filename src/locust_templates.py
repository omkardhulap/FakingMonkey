import time
from requests import Response

from locust.clients import ResponseContextManager
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
        r = self._prep_read_response(len(key))

        value = self.dao.get(key)

        return self._response_success(r)

    @task(int((1.0 - config.rw_ratio) * 1000))
    def write_task(self):
        key = self.generator.gen_key()
        value = self.generator.gen_value()
        r = self._prep_write_response(len(key) + len(value))

        self.dao.set(key, value)

        return self._response_success(r)

    def _prep_read_response(self, size):
        r = Response()
        r.locust_request_meta = {}
        r.locust_request_meta["method"] = "GET"
        r.locust_request_meta["name"] = "read"
        r.locust_request_meta["start_time"] = time.time()
        r.locust_request_meta["content_size"] = size
        return r

    def _prep_write_response(self, size):
        r = Response()
        r.locust_request_meta = {}
        r.locust_request_meta["method"] = "PUT"
        r.locust_request_meta["name"] = "write"
        r.locust_request_meta["start_time"] = time.time()
        r.locust_request_meta["content_size"] = size
        return r

    def _response_success(self, response):
        diff = (time.time() - response.locust_request_meta["start_time"]) * 1000
        response.locust_request_meta["response_time"] = diff
        r = ResponseContextManager(response)
        r.success()
        return r


class WorkloadClient(Locust):
    task_set = KVAccessTasks
    min_wait = 1000
    max_wait = 1000

    def __init__(self):
        super(Locust, self).__init__()
        self.min_wait = 1000 / config.op_rate
        self.max_wait = 1000 / config.op_rate
