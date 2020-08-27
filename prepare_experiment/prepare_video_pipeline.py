import pocket_api
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("config")
args = parser.parse_args()

with open(args.config, 'r') as f:
    content = json.load(f)

dirs = content['dirs']
namenode_ip = "10.1.0.10"
p = pocket_api.connect(namenode_ip, 9070)
for d in dirs:
    pocket_api.create_dir(p, d, "")
