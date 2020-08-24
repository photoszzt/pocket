import os
import sys
import subprocess
import time
import re
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("config")
args = parser.parse_args()

ssh_file = os.path.expanduser("~/.ssh/id_rsa.pub")
if not os.path.exists(ssh_file):
    print("public key file doesn't exist; please generate it")
    sys.exit(1)

script_dir = os.path.dirname(os.path.realpath(__file__))
k8s_cmd = os.path.join(script_dir, 'setup_cluster.sh')

config_file = os.path.expanduser(args.config)
print(k8s_cmd, config_file)
subprocess.run([k8s_cmd, config_file])

with open(args.config, 'r') as f:
    config = json.load(f)
state = config['KOPS_STATE_STORE']
os.environ["KOPS_STATE_STORE"] = state
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

os.system("python3 patch_cluster.py")

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
ip = ip.replace("-", ".")

cmd = 'ssh admin@{} "sudo ip address add 10.1.0.10/17 dev eth1;sudo ip route add default via 10.1.0.1 dev eth1 tab 2;sudo ip rule add from 10.1.0.10/32 tab 2 priority 700"'.format(ip)
print(cmd)
os.system(cmd)

os.system("python3 deploy_pocket_namenode.py")

sys.exit(0)
