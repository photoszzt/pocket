import os
import time
import pocket
import random
import string
import subprocess


def pocket_write(p, jobid, iter, src_filename):
    for i in range(iter):
        dst_filename = 'tmp'+'-'+str(i)
        r = pocket.put(p, src_filename, dst_filename, jobid)
        if r != 0:
            raise Exception("put failed: " + dst_filename)


def pocket_read(p, jobid, iter, src_filename):
    for i in range(iter):
        dst_filename = 'tmp'+'-'+str(i)
        r = pocket.get(p, dst_filename, src_filename, jobid)
        if r != 0:
            raise Exception("get failed: " + dst_filename)


def pocket_lookup(p, jobid, iter):
    for i in range(iter):
        dst_filename = 'tmp'+'-'+str(i)
        r = pocket.lookup(p, dst_filename, jobid)
        if r != 0:
            raise Exception("lookup failed: " + dst_filename)


def pocket_write_buffer(p, jobid, iter, src, size):
    for i in range(iter):
        dst_filename = 'tmp'+'-'+str(i)
        r = pocket.put_buffer(p, src, dst_filename, jobid)
        if r != 0:
            raise Exception("put buffer failed: " + dst_filename)


def pocket_read_buffer(p, jobid, iter, text_back_tmp, size):
    text_back = " "*size
    for i in range(iter):
        dst_filename = 'tmp'+'-'+str(i)
        r = pocket.get_buffer(p, dst_filename, text_back, size, jobid)
        if r != 0:
            raise Exception("get buffer failed: " + dst_filename)


def pocket_read_buffer_bytes(p, jobid, iter):
    for i in range(iter):
        dst_filename = 'tmp'+'-'+str(i)
        _ = pocket.get_buffer_bytes(p, dst_filename, jobid)


def rand_str(slen):
    return ''.join(random.choice(string.ascii_lowercase + string.digits)
                   for _ in range(slen))


def lambda_handler(event, context):
    # create a file of size (datasize) in bytes
    iter = 50000
    datasize = 1024  # bytes
    jobid = "latency-test"
    namenode_ip = "10.1.0.10"

    file_tmp = '/tmp/file_tmp'
    with open(file_tmp, 'w') as f:
        text = 'a'*datasize
        f.write(text)

    # connect to pocket
    p = pocket.connect(namenode_ip, 9070)

    # test read/write through buffer
    dir = jobid + "microbenchmark" + rand_str(4)
    pocket.create_dir(p, dir, "")
    jobid = dir

    t0 = time.time()
    pocket_write_buffer(p, jobid, iter, text, datasize)
    t1 = time.time()
    print("==========================================")
    print("Stats for "+str(iter)+" iter of " +
          str(datasize)+" bytes write_buffer:")
    throughput = iter*datasize*8/(t1-t0)/1e9
    print("throughput (Gb/s) = " + str(throughput))
    print("latency (us) = " + str((t1-t0)/iter*1e6))
    print("==========================================")

    list_dir = pocket.list_dir(p, None, jobid)
    list_dir_list = [f for f in list_dir]
    print(list_dir_list)
    count = pocket.count_files(p, None, jobid)
    print(f'num files: {count}')
    try:
        list_file = pocket.list_dir(p, 'tmp-0', jobid)
    except RuntimeError as e:
        stre = str(e)
        if stre != 'node is not a directory':
            raise

    text_back = " "*datasize
    t0 = time.time()
    pocket_read_buffer(p, jobid, iter, text_back, datasize)
    t1 = time.time()
    print("==========================================")
    print("Stats for "+str(iter)+" iter of " +
          str(datasize)+" bytes read_buffer:")
    throughput = iter*datasize*8/(t1-t0)/1e9
    print("throughput (Gb/s) = " + str(throughput))
    print("latency (us) = " + str((t1-t0)/iter*1e6))
    print("==========================================")

    t0 = time.time()
    pocket_read_buffer_bytes(p, jobid, iter)
    t1 = time.time()
    print("==========================================")
    print("Stats for "+str(iter)+" iter of " +
          str(datasize)+" bytes read_buffer_bytes:")
    throughput = iter*datasize*8/(t1-t0)/1e9
    print("throughput (Gb/s) = " + str(throughput))
    print("latency (us) = " + str((t1-t0)/iter*1e6))
    print("==========================================")

    t0 = time.time()
    pocket_lookup(p, jobid, iter)
    t1 = time.time()
    print("==========================================")
    print("Stats for "+str(iter)+" iter of " +
          str(datasize)+" bytes lookup (metadata RPC):")
    throughput = iter*datasize*8/(t1-t0)/1e9
    print("throughput (Gb/s) = " + str(throughput))
    print("latency (us) = " + str((t1-t0)/iter*1e6))
    print("==========================================")

    os.remove(file_tmp)
    return


if __name__ == '__main__':
    print("main")
    lambda_handler({}, {})
