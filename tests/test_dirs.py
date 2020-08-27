import pocket_api

namenode_ip = "10.1.0.10"
p = pocket_api.connect(namenode_ip, 9070)

pocket_api.create_dirs(p, "b/c", "")

listed = pocket_api.list_dir(p, "/", "")
files = [f for f in listed]
print(files)
listed = pocket_api.list_dir(p, "/b", "")
files = [f for f in listed]
print(files)

pocket_api.delete(p, "/b/c", "")
pocket_api.delete(p, "/b", "")
print("after delete")
listed = pocket_api.list_dir(p, "/", "")
files = [f for f in listed]
print(files)

listed = pocket_api.list_dir(p, "/b", "")
files = [f for f in listed]
print(files)
