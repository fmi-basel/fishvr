import json

file = "vrinfo.json"

with open(file) as f:
    info = json.load(f)
    f.close()

# print(info['timestamp'])
# print(info['trials'][0])