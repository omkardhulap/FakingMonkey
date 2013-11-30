
from random import randint

import config


class StringGenerator:

    def __init__(self):
        self.chars = string.letters + string.digits

    def gen_key(self):
        return self.gen_string(config.key_size)

    def gen_value(self):
        return self.gen_string(config.value_size)

    def gen_string(self, size):
        return ''.join(random.choice(self.chars) for x in xrange(size)
        
