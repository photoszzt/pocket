import subprocess
import os
import time


os.system("kubectl delete job --all")
os.system("kubectl delete deployment --all")
os.system("python3 deploy_pocket_namenode.py")

while True:
    result = subprocess.run("kubectl get pods -o wide".split(), stdout=subprocess.PIPE)
    lines = result.stdout.decode("utf-8")
    lines = lines.split("\n")

    namenode_running = False
    for line in lines:
        if "Running" in line and "pocket-namenode-deployment" in line:
            namenode_running = True
            break
    if namenode_running:
        break
    else:
        time.sleep(2)

num_dram_node = 3
os.system(f"python3 create_datanode_job.py dram {num_dram_node}")
while True:
    result = subprocess.run("kubectl get pods -o wide".split(), stdout=subprocess.PIPE)
    lines = result.stdout.decode("utf-8")
    lines = lines.split("\n")

    num_dram_running = 0
    for line in lines:
        if "Running" in line and "pocket-datanode-dram-jobdram" in line:
            num_dram_running += 1
            if num_dram_running == num_dram_node:
                break
    if num_dram_running == num_dram_node:
        break
    else:
        time.sleep(2)
