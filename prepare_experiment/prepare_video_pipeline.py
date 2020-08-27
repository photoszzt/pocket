import json
import argparse
from string import ascii_lowercase
import pocket_api

parser = argparse.ArgumentParser()
parser.add_argument("config")
args = parser.parse_args()

with open(args.config, 'r') as f:
    content = json.load(f)

dirs = content['dirs']
temp_base = content['temp_base']
namenode_ip = "10.1.0.10"
p = pocket_api.connect(namenode_ip, 9070)
for d in dirs:
    pocket_api.create_dir(p, d, "")

for c in ascii_lowercase:
    pocket_api.create_dir(p, f"{temp_base}{c}", "")
for n in range(9):
    pocket_api.create_dir(p, f"{temp_base}{n}", "")
