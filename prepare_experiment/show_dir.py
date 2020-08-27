import pocket_api

namenode_ip = "10.1.0.10"
p = pocket_api.connect(namenode_ip, 9070)
listed = pocket_api.list_dir(p, "/", "")
files = [f for f in listed]
print(files)
