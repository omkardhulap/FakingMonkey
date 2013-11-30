
import sys
import argparse
from locust import main, TaskSet

import locust_templates as templates
import config


def generate_locust_classes():
    # Build a dict of (classname, class object) pairs for available locusts
    locusts = dict()
    locust_template = templates.WorkloadClient
    taskset_template = templates.KVAccessTasks


    #locust = type("A", (locust_template,), {})
    #locust.tasks = {taskset_template.read_task: 1, taskset_template.write_task: 1}

    locusts["locust"] = locust_template

    return locusts


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
    locust_args.append('--clients=%d' % (2))
    locust_args.append('--hatch-rate=%d' % (1))
    locust_args.append('--num-request=%d' % (1))
    # Override the command line args
    sys.argv = locust_args

    # Dynamically generate our locust classes
    locusts = generate_locust_classes()

    # Inject our locust classes
    def find_locustfile_override(locustfile):
        return True
    def load_locustfile_override(path):
        return None, locusts
    main.find_locustfile = lambda locustfile: True
    main.load_locustfile = load_locustfile_override

    # Finally start the locust system
    main.main()


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
    parser.add_argument('--rw-ratio', type=int, required=False, help='read/write ratio')
    parser.add_argument('--op-rate', type=int, required=False, help='operation rate')
    parser.add_argument('--key-skew', type=int, required=False, help='skew of key accesses')
    parser.add_argument('--key-size', type=int, required=False, help='size in bytes of the keys')

    args = parser.parse_args()
    set_config(args)

    start_monkey()


if __name__ == "__main__":
    monkey_main()
