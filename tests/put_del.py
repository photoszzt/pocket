import random
import string
import pocket_api


def rand_str(size):
    return ''.join([random.choice(string.ascii_letters) for i in range(size)])


def main():
    namenode_ip = "10.1.0.10"
    p = pocket_api.connect(namenode_ip, 9070)
    size = 1 * 1024 * 1024
    chars = rand_str(size)
    jobid = rand_str(3)
    res = pocket_api.create_dir(p, '', jobid)
    for i in range(1000):
        pocket_api.put_buffer(p, "{}".format(i), chars, jobid)
    for i in range(1000):
        pocket_api.delete(p, "{}".format(i), jobid)


if __name__ == '__main__':
    main()
