#######################################################
##  Python library/API to communicate with Pocket    ##
#######################################################
import socket
import struct
import os
from typing import Union
try:
    from . import libpocket
except ImportError:
    import libpocket
try:
    from .libpocket import PocketDispatcher
except ImportError:
    from libpocket import PocketDispatcher

PORT = 2345
HOSTNAME = "localhost"

CONTROLLER_IP = "10.1.47.178"
CONTROLLER_PORT = 4321

MAX_DIR_DEPTH = 16

INT = 4
LONG = 8
FLOAT = 4
SHORT = 2
BYTE = 1

# msg_len (INT), ticket (LONG LONG), cmd (SHORT), cmd_type (SHORT), register_type (BYTE)
REQ_STRUCT_FORMAT = "!iqhhi"
# CMD, CMD_TYPE, IOCTL_OPCODE (note: doesn't include msg_len or ticket from NaRPC hdr)
REQ_LEN_HDR = SHORT + SHORT + INT

# msg_len (INT), ticket (LONG LONG), cmd (SHORT), error (SHORT), register_opcode (BYTE)
RESP_STRUCT_FORMAT = "!iqhhi"
# MSG_LEN, TICKET, CMD, ERROR, REGISTER_OPCODE
RESP_LEN_BYTES = INT + LONG + SHORT + SHORT + INT

TICKET = 1000
RPC_JOB_CMD = 14
JOB_CMD = 14
REGISTER_OPCODE = 0
DEREGISTER_OPCODE = 1


def launch_dispatcher_from_lambda():
    return


def launch_dispatcher(crail_home_path):
    return


def register_job(jobname: str, num_lambdas=0, capacityGB=0, peakMbps=0, latency_sensitive=1):
    # connect to controller
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((CONTROLLER_IP, CONTROLLER_PORT))

    # send register request to controller
    msg_packer = struct.Struct(
        REQ_STRUCT_FORMAT + "i" + str(len(jobname)) + "s" + "iiih")
    msgLen = REQ_LEN_HDR + INT + len(jobname) + 3*INT + SHORT
    sampleMsg = (msgLen, TICKET, RPC_JOB_CMD, JOB_CMD, REGISTER_OPCODE, len(jobname), jobname,
                 num_lambdas, int(capacityGB), int(peakMbps), latency_sensitive)
    pkt = msg_packer.pack(*sampleMsg)
    sock.sendall(pkt)

    # get jobid response
    data = sock.recv(RESP_LEN_BYTES + INT)
    resp_packer = struct.Struct(RESP_STRUCT_FORMAT + "i")
    [length, ticket, type_, err, opcode, jobIdNum] = resp_packer.unpack(data)
    if err != 0:
        jobid = None
        print("Error registering job: ", err)
    else:
        jobid = jobname + "-" + str(jobIdNum)
        print("Registered jobid ", jobid)
    sock.close()
    return jobid


def deregister_job(jobid: str):
    # connect to controller
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((CONTROLLER_IP, CONTROLLER_PORT))

    # send register request to controller
    # len(jobname) (INT) + jobname (STRING)
    msg_packer = struct.Struct(REQ_STRUCT_FORMAT + "i" + str(len(jobid)) + "s")
    msgLen = REQ_LEN_HDR + INT + len(jobid)
    sampleMsg = (msgLen, TICKET, RPC_JOB_CMD, JOB_CMD,
                 DEREGISTER_OPCODE, len(jobid), jobid)
    pkt = msg_packer.pack(*sampleMsg)
    sock.sendall(pkt)

    # get jobid response
    data = sock.recv(RESP_LEN_BYTES)
    resp_packer = struct.Struct(RESP_STRUCT_FORMAT)
    [length, ticket, type_, err, opcode] = resp_packer.unpack(data)
    if err != 0:
        print("Error deregistering job: ", err)
    else:
        print("Successfully deregistered jobid ", jobid)
    sock.close()
    return err


def connect(hostname: str, port: int):
    pocketHandle = libpocket.PocketDispatcher()
    res = pocketHandle.Initialize(hostname, port)
    if res != 0:
        print("Connecting to metadata server failed!")

    return pocketHandle


def put(pocket: PocketDispatcher, src_filename: str, dst_filename: str, jobid: str,
        PERSIST_AFTER_JOB=False, enumerable=False):
    '''
    Send a PUT request to Pocket to write key

    :param pocket:           pocketHandle returned from connect()
    :param str src_filename: name of local file containing data to PUT
    :param str dst_filename: name of file/key in Pocket which writing to
    :param str jobid:        id unique to this job, used to separate
                             keyspace for job
    :param PERSIST_AFTER_JOB:optional hint, if True, data written
                             to table persisted after job done
    :return: the Pocket dispatcher response
    '''

    if jobid:
        jobid = "/" + jobid

    if PERSIST_AFTER_JOB:
        set_filename = jobid + "-persist/" + dst_filename
    else:
        set_filename = jobid + "/" + dst_filename

    res = pocket.PutFile(src_filename, set_filename, enumerable)

    return res


def put_buffer(pocket: PocketDispatcher, src: Union[str, bytes], dst_filename: str,
               jobid: str, PERSIST_AFTER_JOB=False, enumerable=False):
    '''
    Send a PUT request to Pocket to write key

    :param pocket:           pocketHandle returned from connect()
    :param str src: 	   name of local object containing data to PUT
    :param str dst_filename: name of file/key in Pocket which writing to
    :param str jobid:        id unique to this job, used to separate
                             keyspace for job
    :param PERSIST_AFTER_JOB:optional hint, if True, data written
                             to table persisted after job done
    :return: the Pocket dispatcher response
    '''

    if jobid:
        jobid = "/" + jobid

    if PERSIST_AFTER_JOB:
        set_filename = jobid + "-persist/" + dst_filename
    else:
        set_filename = jobid + "/" + dst_filename

    res = pocket.PutBuffer(src, set_filename, enumerable)

    return res


def get(pocket: PocketDispatcher, src_filename: str, dst_filename: str, jobid: str,
        DELETE_AFTER_READ=True):
    '''
    Send a GET request to Pocket to read key

    :param pocket:           pocketHandle returned from connect()
    :param str src_filename: name of file/key in Pocket from which reading
    :param str dst_filename: name of local file where want to store data from GET
    :param str jobid:        id unique to this job, used to separate keyspace for job
    :param DELETE_AFTER_READ:optional hint, if True, data deleted after job done
    :return: the Pocket dispatcher response
    '''

    if jobid:
        jobid = "/" + jobid

    get_filename = jobid + "/" + src_filename

    res = pocket.GetFile(get_filename, dst_filename)
    if res != 0:
        raise Exception(f"GET {get_filename} to {dst_filename} failed!")

    if DELETE_AFTER_READ:
        res = delete(pocket, src_filename, jobid)

    return res


def get_buffer(pocket: PocketDispatcher, src_filename: str, dst: str, len: int, jobid: str,
               DELETE_AFTER_READ=True):
    '''
    Send a GET request to Pocket to read key

    :param pocket:           pocketHandle returned from connect()
    :param str src_filename: name of file/key in Pocket from which reading
    :param str dst: name of local object  where want to store data from GET
    :param str jobid:        id unique to this job, used to separate keyspace for job
    :param DELETE_AFTER_READ:optional hint, if True, data deleted after job done
    :return: the Pocket dispatcher response
    '''

    if jobid:
        jobid = "/" + jobid

    get_filename = jobid + "/" + src_filename

    res = pocket.GetBuffer(dst, len, get_filename)
    if res != 0:
        raise Exception(f"GET BUFFER {get_filename} failed!")

    if DELETE_AFTER_READ:
        res = delete(pocket, src_filename, jobid)

    return res


def get_buffer_bytes(pocket: PocketDispatcher, src_filename: str, jobid: str,
                     DELETE_AFTER_READ=True):
    '''
    Send a GET request to Pocket to read key

    :param pocket:           pocketHandle returned from connect()
    :param str src_filename: name of file/key in Pocket from which reading
    :param str jobid:        id unique to this job, used to separate keyspace for job
    :param DELETE_AFTER_READ:optional hint, if True, data deleted after job done
    :return: the Pocket dispatcher response
    '''
    if jobid:
        jobid = "/" + jobid

    get_filename = jobid + "/" + src_filename

    dst = pocket.GetBufferBytes(get_filename)

    res = 0
    if DELETE_AFTER_READ:
        res = delete(pocket, src_filename, jobid)

    return dst, res


def lookup(pocket: PocketDispatcher, src_filename: str, jobid: str):
    '''
    Send a LOOKUP metadata request to Pocket to see if file exists

    :param pocket:           pocketHandle returned from connect()
    :param str src_filename: name of file/key in Pocket from which looking up
    :param str jobid:        id unique to this job, used to separate keyspace for job
    :return: the Pocket dispatcher response
    '''

    if jobid:
        jobid = "/" + jobid

    get_filename = jobid + "/" + src_filename

    res = pocket.Lookup(get_filename)
    if res != 0:
        print("LOOKUP failed!")

    return res


def delete(pocket: PocketDispatcher, src_filename: str, jobid: str):
    '''
    Send a DEL request to Pocket to delete key

    :param pocket:           pocketHandle returned from connect()
    :param str src_filename: name of file/key in Pocket which deleting
    :param str jobid:        id unique to this job, used to separate keyspace for job
    :return: the Pocket dispatcher response
    '''

    if jobid:
        jobid = "/" + jobid

    if src_filename:
        src_filename = jobid + "/" + src_filename
    else:
        src_filename = jobid

    res = pocket.DeleteDir(src_filename)  # recursive delete

    return res


def create_dir(pocket: PocketDispatcher, src_filename: str, jobid: str):
    '''
    Send a CREATE DIRECTORY request to Pocket

    :param pocket:           pocketHandle returned from connect()
    :param str src_filename: name of directory to create in Pocket
    :param str jobid:        id unique to this job, used to separate keyspace for job
    :return: the Pocket dispatcher response
    '''

    if jobid:
        jobid = "/" + jobid

    if src_filename:
        src_filename = jobid + "/" + src_filename
    else:
        src_filename = jobid

    res = pocket.MakeDir(src_filename)

    return res


def count_files(pocket: PocketDispatcher, dirname: str, jobid: str):
    '''
    Send a COUNT FILES IN A DIRECTORY request to Pocket

    :param pocket:           pocketHandle returned from connect()
    :param str dirname: name of directory to create in Pocket
    :param str jobid:        id unique to this job, used to separate keyspace for job
    :return: the Pocket dispatcher response
    '''

    if jobid:
        jobid = "/" + jobid

    if dirname:
        dirname = jobid + "/" + dirname
    else:
        dirname = jobid

    res = pocket.CountFiles(dirname)

    return res


def close(pocket: PocketDispatcher):
    '''
    Send a CLOSE request to PocketFS

    :param pocket:           pocketHandle returned from connect()
    :return: the Pocket dispatcher response
    '''
    return pocket.Close()  # TODO


def list_dir(pocket: PocketDispatcher, dirname: str, jobid: str):
    '''
    Send a ENUMERATE FILES IN A DIRECTORY request to Pocket

    :param pocket:           pocketHandle returned from connect()
    :param str dirname: name of directory to create in Pocket
    :param str jobid:        id unique to this job, used to separate keyspace for job
    :return: the Pocket dispatcher response
    '''

    if jobid:
        jobid = "/" + jobid

    if dirname:
        if dirname.startswith("/"):
            dirname = dirname[1:]
        dirname = jobid + "/" + dirname
    else:
        dirname = jobid

    print(f"pocket api list_dir: {dirname}")
    res = pocket.EnumerateWithReturn(dirname)
    return res


def path_exists(pocket: PocketDispatcher, path: str, jobid: str):
    exists = True
    try:
        lookup(pocket, path, jobid)
    except RuntimeError as e:
        stre = str(e)
        if stre == 'lookup node failed':
            exists = False
    return exists


def create_dirs(pocket, path: str, jobid: str):
    head, tail = os.path.split(path)
    if not tail:
        head, tail = os.path.split(head)
    if head and tail and not path_exists(pocket, head, jobid):
        create_dirs(pocket, head, jobid)
    try:
        create_dir(pocket, path, jobid)
    except Exception:
        pass
