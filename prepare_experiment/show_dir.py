import argparse
import pocket_api


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default="/")
    args = parser.parse_args()
    namenode_ip = "10.1.0.10"
    p = pocket_api.connect(namenode_ip, 9070)
    listed = pocket_api.list_dir(p, args.dir, "")
    files = [f for f in listed]
    print(files)


if __name__ == '__main__':
    main()
