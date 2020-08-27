import pocket_api

namenode_ip = "10.1.0.10"
p = pocket_api.connect(namenode_ip, 9070)
res = pocket_api.lookup(p, "a", "")
print(res)
dir_exists = True
try:
    res = pocket_api.lookup(p, "b", "")
except RuntimeError as e:
    stre = str(e)
    if stre == 'lookup node failed':
        dir_exists = False
print(dir_exists)
