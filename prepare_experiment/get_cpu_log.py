import argparse
import subprocess


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('addrfile')
    args = parser.parse_args()
    with open(args.addrfile, 'r') as fin:
        for line in fin:
            addr = line.strip()
            subprocess.run(["scp", f"admin@{addr}:/home/admin/cpu_stats", f"{addr}_cpu_stats"])


if __name__ == '__main__':
    main()
