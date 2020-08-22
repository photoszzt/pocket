import os
import sys
import subprocess
import time
import re
import json

cmd = "bash ~/setup_env.sh"
os.system(cmd)

os.chdir("/home/ubuntu/pocket/deploy")
os.system("KOPS_RUN_OBSOLETE_VERSION=yes /home/ubuntu/pocket/deploy/setup_cluster.sh")

while True:
    print("Waiting for cluster to be ready")
    result = subprocess.run("kops validate cluster".split(), stdout=subprocess.PIPE)
    lines = result.stdout.decode('utf-8')
    lines = lines.split("\n")

    cluster_ready = False
    for line in lines:
        if "is ready" in line and "Your cluster" in line:
            cluster_ready = True
            break
    if cluster_ready:
        break
    else:
        time.sleep(2)

os.system("python patch_cluster.py")

cmd = 'aws ec2 describe-security-groups'
result = subprocess.run(cmd.split(), stdout=subprocess.PIPE)
lines = result.stdout.decode('utf-8')
d = json.loads(lines)
sgs = d['SecurityGroups']
for sg in sgs:
    if sg['GroupName'] in ['nodes.pocketcluster.k8s.local', 'masters.pocketcluster.k8s.local']:
        group_id = sg['GroupId']
        cmd = 'aws ec2 authorize-security-group-ingress --group-id {} --cidr 0.0.0.0/0 --protocol -1'.format(group_id)
        print("cmd: {}".format(cmd))
        os.system(cmd)


cmd = "kubectl get nodes --show-labels | grep metadata | awk '{print $1}'"
print("cmd: ", cmd)
p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE, stdin=subprocess.PIPE)
p_stdout = p.stdout.read()
p_stderr = p.stderr.read()
ip = p_stdout.decode("utf-8")
print("ip: ", ip)

ip = re.search(r'(\d+-\d+-\d+-\d+)', ip)
ip = ip.group()
ip = ip.replace("-",".")

cmd = 'ssh admin@{} "sudo ip route add default via 10.1.0.1 dev eth1 tab 2;sudo ip rule add from 10.1.0.10/32 tab 2 priority 700"'.format(ip)
print(cmd)
os.system(cmd)

os.system("python deploy_pocket_namenode.py")

sys.exit(0)
