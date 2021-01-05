import struct
import json
import sys

sys.argv.append("../build/main.json")

file = json.loads(open(sys.argv[1], "rb").read().decode())

vector_inputs = {vec:[[] for gate in file[vec][1]] for vec in list(file) if file[vec][0] == 1}
vector_activators = {vec:[[] for gate in file[vec][1]] for vec in list(file) if file[vec][0] != 1}
vector_gate_types = {vec:[gate if gate != -1 else 0 for gate in file[vec][2]] for vec in list(file) if file[vec][0] != 1}
for vec in list(file):
    for i, gate in enumerate(file[vec][1]):
        for output in gate:
            vector_activators[output[0]][output[1]].append([vec, i])

vector_offset_table = {}
last_offset = 0

gateTypes = []
gateParents = []

for vec in list(vector_inputs):
    print(vec)
    vector_offset_table[vec] = last_offset
    last_offset += len(vector_inputs[vec])
    for x in range(len(vector_inputs[vec])):
        gateTypes.append(0)
        gateParents.append(0)

for vec in list(vector_activators):
    vector_offset_table[vec] = last_offset
    last_offset += len(vector_activators[vec])

for vec in list(vector_activators):
    for gate, typ in zip(vector_activators[vec], vector_gate_types[vec]):
        gateTypes.append(typ)
        gateParents.append(len(gate))
        for parent in gate:
            gateParents.append(vector_offset_table[parent[0]] + parent[1])

f = open('data', 'wb')

#gateTypes = [0, 3, 1]
#gateParents = [0, 1, 0, 2, 0, 1]

#f.write(b'\x00\x01A')
inp = struct.pack('<I{}BI{}I'.format(len(gateTypes), len(gateParents)), len(gateTypes), *gateTypes, len(gateParents), *gateParents)
print(inp)
f.write(inp)

f.close()