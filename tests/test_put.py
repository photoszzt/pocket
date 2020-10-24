import pocket_api

namenode_ip = "10.1.0.10"
p = pocket_api.connect(namenode_ip, 9070)
jobid = 'bbb'
res = pocket_api.create_dir(p, '', jobid)
print(res)
print('put with str')
res = pocket_api.put_buffer(p, 'a', 'abf', jobid)
print(res)
ret = pocket_api.lookup(p, 'abf', 'aaa')
ret = pocket_api.get_buffer_bytes(p, 'abf', jobid)
print(ret)

print('put with bytes')
res = pocket_api.put_buffer(p, b'a', 'abe', jobid)
print(res)
ret = pocket_api.lookup(p, 'abe', 'aaa')
print(res)
ret = pocket_api.get_buffer_bytes(p, 'abe', jobid)
print(ret)
