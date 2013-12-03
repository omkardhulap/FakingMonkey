
import random
import string
import logging
import time

import config


log = logging.getLogger('FakingMonkeyCore')
log.setLevel('INFO')

class StringGenerator:

    def __init__(self):
        log.info("Init StringGenerator")
        self.chars = string.letters + string.digits
        self.mu = random.randint(0, len(self.chars) - 1)
        self.sigma = 0.1 + (config.key_skew * len(self.chars) / 3.0)

    def gen_key(self):
        return self._gen_string(config.key_size)

    def gen_value(self):
        return ''.join(random.choice(self.chars) for x in xrange(config.value_size))

    def _gen_string(self, size):
        return ''.join(self._gen_char() for x in xrange(size))

    def _gen_char(self):
        if config.key_skew == 1.0:
            # shortcut to a uniform distribution
            return random.choice(self.chars)
        else:
            # else use a normal distribution
            index = -1
            while index < 0 or index >= len(self.chars):
                index = int(round(random.gauss(self.mu, self.sigma)))
                log.debug("Generated index {}".format(index))
            char = self.chars[index]
            return char
