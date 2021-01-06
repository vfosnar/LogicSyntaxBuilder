import struct
import json
import sys

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

print("Inputs")
for vec in list(vector_inputs):
    vector_offset_table[vec] = last_offset
    last_offset += len(vector_inputs[vec])
    print("{} at {} to {}".format(vec, len(gateTypes), len(gateTypes) + len(vector_inputs[vec])))
    for x in range(len(vector_inputs[vec])):
        gateTypes.append(0)
        gateParents.append(0)

inputSize = last_offset

for vec in list(vector_activators):
    vector_offset_table[vec] = last_offset
    last_offset += len(vector_activators[vec])

print("Outputs")
output = []
for vec in list(vector_activators):
    if(file[vec][0] == 2):
        print("{} at {} to {}".format(vec, len(gateTypes), len(gateTypes) + len(vector_activators[vec])))
        output.append(len(gateTypes))
        output.append(len(gateTypes) + len(vector_activators[vec]))
    for gate, typ in zip(vector_activators[vec], vector_gate_types[vec]):
        gateTypes.append(typ)
        gateParents.append(len(gate))
        for parent in gate:
            gateParents.append(vector_offset_table[parent[0]] + parent[1])

f = open('data', 'wb')
inp = struct.pack('<I{}BI{}I'.format(len(gateTypes), len(gateParents)), len(gateTypes), *gateTypes, len(gateParents), *gateParents)
f.write(inp)
f.close()

file_inputs = json.loads(open(sys.argv[2], "rb").read().decode())

inputCount = len(file_inputs)

f_sim = open('sim', 'wb')
inp = struct.pack('<I{}III'.format(len(output)), int(len(output) / 2), *output, inputCount, inputSize)
f_sim.write(inp)
for input_ in file_inputs:
    inputs = [0 for x in range(inputSize)]
    for vec in list(vector_inputs):
        vecPosition = vector_offset_table[vec]
        for gateOffset in range(len(vector_inputs[vec])):
            inputs[vecPosition + gateOffset] = input_[vec][gateOffset]
    f_sim.write(struct.pack('<{}?'.format(inputSize), *inputs))
f_sim.close()