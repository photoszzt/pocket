import random
import string
import pocket_api
import subprocess
import psutil
import gc
import os


def rand_str(size):
    return ''.join([random.choice(string.ascii_letters) for i in range(size)])


def main():
    print("memory usage at the begining {}".format(memory_footprint()))
    namenode_ip = "10.1.0.10"
    p = pocket_api.connect(namenode_ip, 9070)
    size = 1024 * 1024
    chars = rand_str(size)
    jobid = rand_str(3)
    res = pocket_api.create_dir(p, '', jobid)
    print("memory usage before get {}".format(memory_footprint()))
    for i in range(10):
        pocket_api.put_buffer(p, chars, "{}".format(i), jobid)
    print("memory usage before put {}".format(memory_footprint()))
    for i in range(10):
        ret = pocket_api.get_buffer_bytes(p, "{}".format(i), jobid)
        del ret
    print("memory usage after put {}".format(memory_footprint()))
    gc.collect(generation=2)
    print("memory usage after gc {}".format(memory_footprint()))


def memory_footprint():
    '''Returns memory (in MB) being used by Python process'''
    mem = psutil.Process(os.getpid()).memory_info().rss
    return (mem / 1024 ** 2)


if __name__ == '__main__':
    main()
