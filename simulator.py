import json
import sys
from tqdm import tqdm

if __name__ == "__main__":
    global vector_activations
    global file
    file = json.loads(open(sys.argv[1], "rb").read().decode())
    file_inputs = json.loads(open(sys.argv[2], "rb").read().decode())
    times = 50
    if(len(sys.argv) == 4):
        times = sys.argv[3]
    vector_activations = {vec:[False for gate in file[vec][1]] for vec in list(file) if file[vec][0] != 1}
    vector_activators = {vec:[[] for gate in file[vec][1]] for vec in list(file) if file[vec][0] != 1}
    vector_gate_types = {vec:[gate if gate != -1 else 0 for gate in file[vec][2]] for vec in list(file) if file[vec][0] != 1}
    for vec in list(file):
        for i, gate in enumerate(file[vec][1]):
            for output in gate:
                vector_activators[output[0]][output[1]].append([vec, i])
    
    def step(input_vectors):
        new_vector_activations = {}
        old_vector_activations = vector_activations.copy()
        for vec in list(input_vectors):
            old_vector_activations[vec] = input_vectors[vec]
        for vec in list(vector_activations):
            new_vector_activations[vec] = []
            gate_type = None
            for gate_type, inputs in zip(vector_gate_types[vec], vector_activators[vec]):
                neg = False
                if(gate_type >= 3):
                    gate_type -= 3
                    neg = True
                active = False
                if(gate_type == 0): # and
                    active = bool(len(inputs))
                    for gate in inputs:
                        active *= old_vector_activations[gate[0]][gate[1]]
                    active = bool(active)
                elif(gate_type == 1): # or
                    active = 0
                    for gate in inputs:
                        active += old_vector_activations[gate[0]][gate[1]]
                    active = bool(active)
                elif(gate_type == 2): # xor
                    for gate in inputs:
                        active += old_vector_activations[gate[0]][gate[1]]
                    active = bool(active % 2)
                else:
                    raise Exception("Gate is invalid")
                new_vector_activations[vec].append(active^neg)
        return new_vector_activations
    
    def epoch(input_vectors, times):
        global vector_activations
        global file
        progress = False
        if(progress):
            for _ in tqdm(range(times)):
                vector_activations = step(input_vectors)
        else:
            for _ in range(times):
                vector_activations = step(input_vectors)
        if(not "debug_show" in input_vectors):
            return
        for vec in list(vector_activations):
            if(file[vec][0] == 2):
                print("{}:".format(vec))
                sys.stdout.write("|")
                for value in vector_activations[vec]: sys.stdout.write("█") if value else sys.stdout.write("_")
                sys.stdout.write("|")
                sys.stdout.write('\n')
    
    for inputs in file_inputs:
        epoch(inputs, times)