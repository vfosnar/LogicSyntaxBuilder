import sys
import os
import shlex
import json

def generate_absolute_vector_positions(vector_size, string_syntax):
    # is empty -> whole vector is used
    if(string_syntax == ""):
        return [x for x in range(vector_size)]
    if(string_syntax[-1] != "]"):
        raise Exception("Expected vec[formatted_range] at line {}".format(file_line))

    # get rid of []
    string_syntax = string_syntax[1:-1]

    # is normal integer: vec[index]
    try:
        position = int(string_syntax)
        if(position < 0):
            position = vector_size + position
        return [position]
    except:
        pass
    
    string_syntax_split = string_syntax.split(':')

    # is range: vec[int:int]
    if(len(string_syntax_split) == 2):
        range_start = 0
        range_end = vector_size
        
        if(string_syntax_split[0] != ""):
            try:
                range_start = int(string_syntax_split[0])
                if(range_start < 0):
                    range_start = vector_size + range_start
            except:
                raise Exception("Expected vec[range_start:range_end] at line {}".format(file_line))
        
        if(string_syntax_split[1] != ""):
            try:
                range_end = int(string_syntax_split[1])
                if(range_end < 0):
                    range_end = vector_size + range_end
            except:
                raise Exception("Expected vec[range_start:range_end] at line {}".format(file_line))
        return [x for x in range(range_start, range_end)]
    if(len(string_syntax_split) == 3):
        range_start = 0
        range_end = vector_size
        range_step = 1

        if(string_syntax_split[0] != ""):
            try:
                range_start = int(string_syntax_split[0])
                if(range_start < 0):
                    range_start = vector_size + range_start
            except:
                raise Exception("Expected vec[range_start:range_end:range_step] at line {}".format(file_line))
        if(string_syntax_split[1] != ""):
            try:
                range_end = int(string_syntax_split[1])
                if(range_end < 0):
                    range_end = vector_size + range_end
            except:
                raise Exception("Expected vec[range_start:range_end:range_step] at line {}".format(file_line))
        if(string_syntax_split[2] != ""):
            try:
                range_step = int(string_syntax_split[2])
            except:
                raise Exception("Expected vec[range_start:range_end:range_step] at line {}".format(file_line))
        return [x for x in range(range_start, range_end)][::range_step]

operands_table = [
    "and",
    "or",
    "xor",
    "nand",
    "nor",
    "xnor"
]

if __name__ == "__main__":
    #if(len(sys.argv) != 2):
    #    raise Exception("Invalid parameter count")
    vectors_outputs = {} # {"a":[["b", 0]]}
    vectors_gate_types = {}
    vectors_nio_type = {}

    def assign(name, size, vector_type):
        if(size[0] != "["):
            raise Exception("Expected 'vec[size]', 'in vec[size]' or 'out vec[size]' at line {}".format(file_line))
        if(size[-1] != "]"):
            raise Exception("Expected 'vec[size]', 'in vec[size]' or 'out vec[size]' at line {}".format(file_line))
        vector_size = size[1:-1]
        
        vectors_outputs["base_{}".format(name)] = []
        vectors_gate_types["base_{}".format(name)] = []

        vectors_nio_type["base_{}".format(name)] = vector_type

        for _ in range(int(vector_size)):
            vectors_outputs["base_{}".format(name)] += [[]]
            vectors_gate_types["base_{}".format(name)] += [-1] # -1 means undefined

    global_reference_prefix = 0
    reference_json_table = {}

    # btw idk why im keeping variable names in files.. probably gonna change export file and save everything in binary encoding instead of json

    stage = 0
    # 0 find reference or define
    # 1 read references or find define
    #
    file_line = 0
    # file = open(sys.argv[1], 'rb').read().decode().replace('\r', "").split('\n')
    file = open("script", 'rb').read().decode().replace('\r', "").split('\n')

    while file_line < len(file):
        line = file[file_line].split(';')[0] # you can write comments after ';'
        if(line == ""):
            pass
        elif(stage == 0):
            if(line == "reference:"):
                stage = 1
            elif(line == "define:"):
                stage = 2
        elif(stage == 1):
            line_split = shlex.split(line)
            if(line == "define:"):
                stage = 2
            elif(line_split[0] == "use"):
                if(len(line_split) != 4):
                    raise Exception("Expected 3 parameters for 'use' at line {}".format(file_line))
                if(line_split[2] != "as"):
                    raise Exception("Expected 'as' parameter at line {}".format(file_line))
                # Set reference prefix
                reference_prefix = line_split[3]

                reference_data = ""
                try:
                    reference_data = open(line_split[1], 'rb').read().decode()
                except:
                    raise Exception("Can't open file {} at line {}".format(line_split[1], file_line))
                reference_json_data = {}
                try:
                    reference_json_data = json.loads(reference_data)
                except:
                    raise Exception("Can't parse json file {} at line {}".format(line_split[1], file_line))
                
                reference_json_table[line_split[3]] = reference_json_data
            
            else:
                raise Exception("Unexpected symbol at line {}".format(file_line))
        elif(stage == 2):
            line_split = shlex.split(line)
            if(line == "assign:"):
                stage = 3
            elif(len(line_split) == 2):
                if(line_split[0] == "in"):
                    name = line_split[1].split("[")[0]
                    size = line_split[1][len(name):]
                    assign(name, size, 1)
                elif(line_split[0] == "out"):
                    name = line_split[1].split("[")[0]
                    size = line_split[1][len(name):]
                    assign(name, size, 2)
                else:
                    raise Exception("Expected 'vec[size]', 'in vec[size]' or 'out vec[size]' at line {}".format(file_line))
            elif(len(line_split) == 1):
                name = line_split[0].split("[")[0]
                size = line_split[0][len(name):]
                assign(name, size, 0)
                
            else:
                raise Exception("Expected 'vec[size]', 'in vec[size]' or 'out vec[size]' at line {}".format(file_line))

        elif(stage == 3):
            line_split = shlex.split(line)
            if(line_split[1] == "<="):
                # generate absolute vector positions
                # ex. a[:5] -> [0, 1, 2, 3, 4]
                name = line_split[0].split("[")[0]
                formatting = line_split[0][len(name):]
                positions = generate_absolute_vector_positions(len(vectors_outputs["base_{}".format(name)]), formatting)
                
                gate_operation = 0
                name_inp = None
                formatting_out = None

                # read second parameter
                if(len(line_split) == 3):
                    name_inp = line_split[2].split("[")[0]
                    formatting_out = line_split[2][len(name):]
                elif(len(line_split) == 4):
                    # second parameter is modified with operation
                    if(not line_split[2] in operands_table):
                        raise Exception("Unknown operand type at line {}".format(file_line))
                    gate_operation = operands_table.index(line_split[2])
                    name_inp = line_split[3].split("[")[0]
                    formatting_out = line_split[3][len(name):]
                else:
                    raise Exception("Expected 'vec <= vec' or 'vec <= operand vec' at line {}".format(file_line))
                
                if(vectors_nio_type["base_{}".format(name)] == 1):
                    raise Exception("Can't assign to a input vector at line {}".format(file_line))
                
                # generate absolute positions for input vector
                positions_out = generate_absolute_vector_positions(len(vectors_outputs["base_{}".format(name_inp)]), formatting_out)
                if(len(positions) != len(positions_out)):
                    raise Exception("Vectors aren't same size at line {}".format(file_line))
                for index, index_out in zip(positions, positions_out):
                    # set output gates types
                    vectors_gate_types["base_{}".format(name_inp)][index] = gate_operation
                    # add gates to input vecotor's outputs
                    vectors_outputs["base_{}".format(name)][index] += [["base_{}".format(name_inp), index_out]]
                
            elif(len(line_split) == 1 and line_split[0] in list(reference_json_table)):

                # get json code from reference table
                reference_json_data = reference_json_table[line_split[0]]
                

                for vector_name in list(reference_json_data):
                    if(reference_json_data[vector_name][0] in [0, 2]):
                        # when vector is normal or output

                        # define local vectors
                        vectors_outputs["{}_{}".format(global_reference_prefix, vector_name)] = []
                        vectors_gate_types["{}_{}".format(global_reference_prefix, vector_name)] = []

                        # for each gate in vector
                        for reference_vector_outputs, gate_type in zip(reference_json_data[vector_name][1], reference_json_data[vector_name][2]):
                            # add gate to vector
                            vectors_outputs["{}_{}".format(global_reference_prefix, vector_name)] += [[]]
                            # add gate type to gate type vector
                            vectors_gate_types["{}_{}".format(global_reference_prefix, vector_name)] += [gate_type]

                            # for each connection from this gate
                            for reference_vector_output in reference_vector_outputs:
                                # Just set prefix and add connection under gate to local vector ex. ["a", 0] -> ["a_0", 0]
                                vectors_outputs["{}_{}".format(global_reference_prefix, vector_name)][-1] += [["{}_{}".format(global_reference_prefix, reference_vector_output[0]), reference_vector_output[1]]]
                    elif(reference_json_data[vector_name][0] == 1):
                        # when vector is input
                        # inputs cant have defined gate types because gate type changes when referenced and assigned

                        # define local vector
                        vectors_outputs["{}_{}".format(global_reference_prefix, vector_name)] = []
                        # for each gate in vector
                        for reference_vector_outputs in reference_json_data[vector_name][1]:
                            # add gate to vector
                            vectors_outputs["{}_{}".format(global_reference_prefix, vector_name)] += [[]]

                            # for each connection from this gate
                            for reference_vector_output in reference_vector_outputs:
                                # Just set prefix and add connection under gate to local vector ex. ["a", 0] -> ["a_0", 0]
                                vectors_outputs["{}_{}".format(global_reference_prefix, vector_name)][-1] += [["{}_{}".format(global_reference_prefix, reference_vector_output[0]), reference_vector_output[1]]]
                    else:
                        raise Exception("Unknown connection type when parsing json file at line {}".format(file_line))
                stage = 4
                
            else:
                raise Exception("Unexpected symbol at line {}".format(file_line))
        
        elif(stage == 4):
            if(line != '{'):
                raise Exception("Expected '{' at line {}".format(file_line))
            stage = 5
        elif(stage == 5):
            line_split = shlex.split(line)
            if(line == '}'):
                stage = 5
                global_reference_prefix += 1
            elif(len(line_split) == 3):
                pass                                  ########################## TODO ADD REFERENCE CONNECTIONS ETC
            else:
                raise Exception("Expected 'to/exp local_vec <= reference_vec', 'in/out local_vec <= operand reference_vec' or '}' at line {}".format(file_line))

        file_line += 1

pass