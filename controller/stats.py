import asyncio
import pocket_metadata_cmds as ioctlcmd


BLOCKSIZE = 65536		 # this should match setting in Pocket metadata and storage servers
DRAM = 0
STORAGE_TIERS = [DRAM]
CONTROLLER_IP = "10.1.47.178"    # note: the controller IP address is hard-coded in other places
                                 # so when create controller VM in EC2, set its IP to 10.1.47.178
NAMENODE_IP = "10.1.0.10"	 # set this to the metadata server IP
NAMENODE_PORT = 9070

DRAM_NODE_PORT = 50030
GET_CAPACITY_STATS_INTERVAL = 1  # how often get stats from metadata server, in seconds

avg_util = {'cpu': 0, 'net': 0, 'dram': 0, 'flash': 0, 'net_aggr':0, 'dram_totalGB': 0, 'dram_usedGB':0, 'flash_totalGB':0, 'flash_usedGB':0}


@asyncio.coroutine
def get_capacity_stats_periodically(sock):
    while True:
        yield from asyncio.sleep(GET_CAPACITY_STATS_INTERVAL)
        for tier in STORAGE_TIERS:
            all_blocks, free_blocks = yield from ioctlcmd.get_class_stats(sock, tier)
            if all_blocks:
                avg_usage = (all_blocks - free_blocks)*100.0 / all_blocks
                print("Capacity usage for Tier", tier, ":", free_blocks, "free blocks out of", \
                       all_blocks, "(", avg_usage, "% )")
            else:
                avg_usage = -1
            # update global avg_util dictionary
            if tier == 0:
                avg_util['dram'] = avg_usage
                avg_util['dram_totalGB'] = all_blocks * BLOCKSIZE * 1.0 / 1e9
                avg_util['dram_usedGB'] = (all_blocks - free_blocks) * BLOCKSIZE * 1.0 / 1e9


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    metadata_socket = ioctlcmd.connect_until_succeed(NAMENODE_IP, NAMENODE_PORT)
    loop.run_until_complete(get_capacity_stats_periodically(metadata_socket))
