
import sys
import argparse
import logging

from locust import main, TaskSet

import locust_templates as templates
import config


log = logging.getLogger('FakingMonkeyMain')
log.setLevel('INFO')

def start_monkey():
    '''
    read/write ratio
    operation rate
    key access skew
    key size
    '''
    # Pretend that we are invoking locust from the command line
    locust_args = ['locust']
    #locust_args.append('--help')
    locust_args.append('--host=%s' % ('localhost'))
    locust_args.append('--locustfile=%s' % ('locust_templates.py'))
    locust_args.append('--no-web')
    locust_args.append('--clients=%d' % (config.op_rate))
    locust_args.append('--hatch-rate=%d' % (1))
    locust_args.append('--num-request=%d' % (100))
    # Override the command line args
    sys.argv = locust_args


    # Finally start the locust system
    log.info("Starting FakingMonkey")
    main.main()


def check_valid_config():
    if not isinstance(config.rw_ratio, float) or config.rw_ratio > 1.0 or config.rw_ratio < 0:
        raise ValueError("read/write ratio must be a value from 0.0 to 1.0")
    if not isinstance(config.op_rate, int) or config.op_rate < 0:
        raise ValueError("operation rate must be a positive integer")
    if not isinstance(config.key_skew, float) or config.key_skew > 1.0 or config.key_skew < 0:
        raise ValueError("key skew must be a value from 0.0 to 1.0")
    if not isinstance(config.key_size, int) or config.key_size < 0:
        raise ValueError("key size must be a positive integer")
    if not isinstance(config.value_size, int) or config.value_size < 0:
        raise ValueError("value size must be a positive integer")


def set_config(params):
    if 'rw-ratio' in params:
        config.rw_ratio = params['rw_ratio']
    if 'op-rate' in params:
        config.op_rate = params['op-rate']
    if 'key-skew' in params:
        config.key_skew = params['key-skew']
    if 'key-size' in params:
        config.key_size = params['key-size']


def monkey_main():
    parser = argparse.ArgumentParser(description='Fake some K/V workload')
    parser.add_argument('--rw-ratio', type=float, required=False, help='read/write ratio')
    parser.add_argument('--op-rate', type=int, required=False, help='operation rate')
    parser.add_argument('--key-skew', type=float, required=False, help='skew of key accesses')
    parser.add_argument('--key-size', type=int, required=False, help='size in bytes of the keys')

    args = parser.parse_args()
    set_config(args)

    check_valid_config()

    start_monkey()


if __name__ == "__main__":
    monkey_main()
