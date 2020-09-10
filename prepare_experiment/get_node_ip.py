import subprocess
import json


def main():
    result = subprocess.run("kubectl get pods -o json".split(), stdout=subprocess.PIPE)
    lines = result.stdout.decode("utf-8")
    d = json.loads(lines)
    for item in d['items']:
        if 'pocket-datanode-dram' in item['metadata']['name']:
            print(item['status']['hostIP'])


if __name__ == '__main__':
    main()
