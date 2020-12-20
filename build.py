import sys
import os
import shlex
import json

def generate_absolute_vector_positions(vector_size, string_syntax):
    # is empty -> whole vector is used
    if(string_syntax == ""):
        return [x for x in range(vector_size)]
    if(string_syntax[-1] != "]"):
        raise Exception("Expected vec[formatted_range] at line {} in file {}".format(file_line + 1, filename))

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
                raise Exception("Expected vec[range_start:range_end] at line {} in file {}".format(file_line + 1, filename))
        
        if(string_syntax_split[1] != ""):
            try:
                range_end = int(string_syntax_split[1])
                if(range_end < 0):
                    range_end = vector_size + range_end
            except:
                raise Exception("Expected vec[range_start:range_end] at line {} in file {}".format(file_line + 1, filename))
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
                raise Exception("Expected vec[range_start:range_end:range_step] at line {} in file {}".format(file_line + 1, filename))
        if(string_syntax_split[1] != ""):
            try:
                range_end = int(string_syntax_split[1])
                if(range_end < 0):
                    range_end = vector_size + range_end
            except:
                raise Exception("Expected vec[range_start:range_end:range_step] at line {} in file {}".format(file_line + 1, filename))
        if(string_syntax_split[2] != ""):
            try:
                range_step = int(string_syntax_split[2])
            except:
                raise Exception("Expected vec[range_start:range_end:range_step] at line {} in file {}".format(file_line + 1, filename))
        return [x for x in range(range_start, range_end)][::range_step]

def bitfield(n):
    return [1 if digit=='1' else 0 for digit in bin(n)[2:]]

operands_table = [
    "and",
    "or",
    "xor",
    "nand",
    "nor",
    "xnor"
]

if __name__ == "__main__":
    if(len(sys.argv) < 2):
        raise Exception("Invalid parameter count")
    for filename in sys.argv[1:]:
        vectors_outputs = {} # {"a":[["b", 0]]}
        vectors_gate_types = {}
        vectors_nio_type = {}

        def assign(name, size, vector_type):
            if(size[0] != "["):
                raise Exception("Expected 'vec[size]', 'in vec[size]' or 'out vec[size]' at line {} in file {}".format(file_line + 1, filename))
            if(size[-1] != "]"):
                raise Exception("Expected 'vec[size]', 'in vec[size]' or 'out vec[size]' at line {} in file {}".format(file_line + 1, filename))
            vector_size = size[1:-1]
            
            vectors_outputs["_{}".format(name)] = []
            vectors_gate_types["_{}".format(name)] = []

            vectors_nio_type["_{}".format(name)] = vector_type

            for _ in range(int(vector_size)):
                vectors_outputs["_{}".format(name)] += [[]]
                vectors_gate_types["_{}".format(name)] += [-1] # -1 means undefined

        assign("_const_0_1", "[1]", 0)

        global_reference_prefix = 0
        reference_json_table = {}

        # this is used only to check if vector is input in reference
        reference_input_list = []
        # same to outputs
        reference_output_list = []

        # btw idk why im keeping variable names in files.. probably gonna change export file and save everything in binary encoding instead of json

        stage = 0
        # 0 find reference or define
        # 1 read references or find define
        #
        file_line = 0
        file = open(filename, 'rb').read().decode().replace('\r', "").split('\n')

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
                        raise Exception("Expected 3 parameters for 'use' at line {} in file {}".format(file_line + 1, filename))
                    if(line_split[2] != "as"):
                        raise Exception("Expected 'as' parameter at line {} in file {}".format(file_line + 1, filename))
                    # Set reference prefix
                    reference_prefix = line_split[3]

                    reference_data = ""
                    try:
                        reference_data = open(line_split[1], 'rb').read().decode()
                    except:
                        raise Exception("Can't open file {} at line {} in file {}".format(line_split[1], file_line + 1, filename))
                    reference_json_data = {}
                    try:
                        reference_json_data = json.loads(reference_data)
                    except:
                        raise Exception("Can't parse json file {} at line {} in file {}".format(line_split[1], file_line + 1, filename))
                    
                    reference_json_table[line_split[3]] = reference_json_data
                
                else:
                    raise Exception("Unexpected symbol at line {} in file {}".format(file_line + 1, filename))
            elif(stage == 2):
                line_split = shlex.split(line)
                if(line == "assign:"):
                    stage = 3
                elif(len(line_split) == 2):
                    if(line_split[0] == "in"):
                        name_left = line_split[1].split("[")[0]
                        size = line_split[1][len(name_left):]
                        assign(name_left, size, 1)
                    elif(line_split[0] == "out"):
                        name_left = line_split[1].split("[")[0]
                        size = line_split[1][len(name_left):]
                        assign(name_left, size, 2)
                    else:
                        raise Exception("Expected 'vec[size]', 'in vec[size]' or 'out vec[size]' at line {} in file {}".format(file_line + 1, filename))
                elif(len(line_split) == 1):
                    name_left = line_split[0].split("[")[0]
                    size = line_split[0][len(name_left):]
                    assign(name_left, size, 0)
                    
                else:
                    raise Exception("Expected 'vec[size]', 'in vec[size]' or 'out vec[size]' at line {} in file {}".format(file_line + 1, filename))

            elif(stage == 3):
                line_split = shlex.split(line)
                if(len(line_split) >= 3 and line_split[1] == "<="):
                    # generate absolute vector positions
                    # ex. a[:5] -> [0, 1, 2, 3, 4]
                    name_left = line_split[0].split("[")[0]
                    formatting_left = line_split[0][len(name_left):]
                    positions_left = generate_absolute_vector_positions(len(vectors_outputs["_{}".format(name_left)]), formatting_left)
                    
                    gate_operation = 0
                    names_right = []
                    formattings_right = []

                    # read second parameter
                    if(len(line_split) == 3):
                        names_right = [line_split[2].split("[")[0]]
                        formattings_right = [line_split[2][len(names_right[-1]):]]
                    elif(len(line_split) >= 4):
                        # second parameter is modified with operation
                        if(not line_split[2] in operands_table):
                            raise Exception("Unknown operand type at line {} in file {}".format(file_line + 1, filename))
                        gate_operation = operands_table.index(line_split[2])
                        for x in range(3, len(line_split)):
                            names_right += [line_split[x].split("[")[0]]
                            formattings_right += [line_split[x][len(names_right[-1]):]]
                    else:
                        raise Exception("Expected 'vec <= vec' or 'vec <= operand vec' at line {} in file {}".format(file_line + 1, filename))
                    
                    if(vectors_nio_type["_{}".format(name_left)] == 1):
                        raise Exception("Can't assign to a input vector at line {} in file {}".format(file_line + 1, filename))
                    
                    # check gate types
                    for index_left in positions_left:
                        try:
                            if(vectors_gate_types["_{}".format(name_left)][index_left] != -1):
                                raise Exception("Vector range is already assigned at line {} in file {}".format(file_line + 1, filename))
                        except IndexError:
                            raise Exception("Index is out of range in vector at line {} in file {}".format(file_line + 1, filename))
                    
                    # foreach vector on right side
                    for name_right, formatting_right in zip(names_right, formattings_right):
                        ##### check if vector isnt actually a constant, if it is then add this constant to vectors #####
                        if(formatting_right == ""):
                            try:
                                value = int(name_right)
                                if(not "__const_{}_{}".format(name_right, len(positions_left)) in vectors_outputs): # contstant isnt already defined
                                    vectors_outputs["__const_{}_{}".format(name_right, len(positions_left))] = []
                                    vectors_gate_types["__const_{}_{}".format(name_right, len(positions_left))] = []
                                    vectors_nio_type["__const_{}_{}".format(name_right, len(positions_left))] = 0
                                    bf = bitfield(value)[::-1]                                  # generate list of bits from constant
                                    for _ in range(len(positions_left) - len(bf)): bf.append(0) # add items to list if its too small
                                    bf = bf[:len(positions_left)]                               # remove items if its too long
                                    for i in range(len(positions_left)):
                                        vectors_outputs["__const_{}_{}".format(name_right, len(positions_left))] += [[]]
                                        vectors_gate_types["__const_{}_{}".format(name_right, len(positions_left))] += [bf[i]*4] # if its 0 => 0 if its 1 => 4; nand
                                        vectors_outputs["__const_0_1"][0] += [["__const_{}_{}".format(name_right, len(positions_left)), i]]
                                name_right = "_const_{}_{}".format(name_right, len(positions_left))
                            except ValueError:
                                pass
                        # generate absolute positions for vector
                        positions_right = generate_absolute_vector_positions(len(vectors_outputs["_{}".format(name_right)]), formatting_right)
                        # calculate how many times iterate over vector
                        iterate = max(len(positions_left), len(positions_right))
                        if(len(positions_left) != len(positions_right)):
                            print("Warning: Vectors aren't same size at line {} in file {}".format(file_line + 1, filename))

                        # for connection in left vector and right vector
                        for i in range(iterate):
                            index_left = positions_left[i % len(positions_left)]
                            # Get gate in right vector
                            index_right = positions_right[i % len(positions_right)]
                            
                            # set output gates types
                            vectors_gate_types["_{}".format(name_left)][index_left] = gate_operation
                            # add gates to input vecotor's outputs
                            vectors_outputs["_{}".format(name_right)][index_right] += [["_{}".format(name_left), index_left]]
                    
                elif(len(line_split) == 1 and line_split[0] in list(reference_json_table)):

                    # get json code from reference table
                    reference_json_data = reference_json_table[line_split[0]]
                    
                    # clear list for this reference
                    reference_input_list = []
                    reference_output_list = []

                    for vector_name in list(reference_json_data):
                        if(reference_json_data[vector_name][0] in [0, 2]):
                            # when vector is normal or output

                            # define local vectors
                            vectors_outputs["{}_{}".format(global_reference_prefix, vector_name)] = []
                            vectors_gate_types["{}_{}".format(global_reference_prefix, vector_name)] = []
                            vectors_nio_type["{}_{}".format(global_reference_prefix, vector_name)] = 0
                            if(reference_json_data[vector_name][0] == 2):
                                reference_output_list += [vector_name]

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
                            vectors_gate_types["{}_{}".format(global_reference_prefix, vector_name)] = [-1 for _ in range(len(reference_json_data[vector_name][1]))]
                            vectors_nio_type["{}_{}".format(global_reference_prefix, vector_name)] = 0

                            reference_input_list += [vector_name]

                            # for each gate in vector
                            for reference_vector_outputs in reference_json_data[vector_name][1]:
                                # add gate to vector
                                vectors_outputs["{}_{}".format(global_reference_prefix, vector_name)] += [[]]

                                # for each connection from this gate
                                for reference_vector_output in reference_vector_outputs:
                                    # Just set prefix and add connection under gate to local vector ex. ["a", 0] -> ["a_0", 0]
                                    vectors_outputs["{}_{}".format(global_reference_prefix, vector_name)][-1] += [["{}_{}".format(global_reference_prefix, reference_vector_output[0]), reference_vector_output[1]]]
                        else:
                            raise Exception("Unknown connection type when parsing json file at line {} in file {}".format(file_line + 1, filename))
                    stage = 4
                    
                else:
                    raise Exception("Unexpected symbol at line {} in file {}".format(file_line + 1, filename))
            
            elif(stage == 4):
                if(line != '{'):
                    raise Exception("Expected opening curly bracket at line {} in file {}".format(file_line + 1, filename))
                stage = 5
            elif(stage == 5):
                line_split = shlex.split(line)
                if(line == '}'):
                    stage = 3
                    global_reference_prefix += 1
                elif(len(line_split) >= 4):
                    # default is export, will read vectors inside reference into local vectors
                    name_left_prefix = ""
                    name_right_prefix = global_reference_prefix

                    if(line_split[0] == "to"): # will write from local vectors to those in reference
                        name_left_prefix, name_right_prefix = name_right_prefix, name_left_prefix
                    elif(line_split[0] != "exp"): # isn't export neither
                        raise Exception("Expected to/exp at line {} in file {}".format(file_line + 1, filename))

                    # generate absolute vector positions
                    # ex. a[:5] -> [0, 1, 2, 3, 4]
                    name_left = line_split[1].split("[")[0]
                    formatting_left = line_split[1][len(name_left):]
                    positions_left = generate_absolute_vector_positions(len(vectors_outputs["{}_{}".format(name_left_prefix, name_left)]), formatting_left)
                    
                    gate_operation = 0
                    names_right = []
                    formattings_right = []

                    # read second parameter
                    if(len(line_split) == 4):
                        names_right = [line_split[3].split("[")[0]]
                        formattings_right = [line_split[3][len(names_right[-1]):]]
                    elif(len(line_split) >= 5):
                        # second parameter is modified with operation
                        if(not line_split[3] in operands_table):
                            raise Exception("Unknown operand type at line {} in file {}".format(file_line + 1, filename))
                        gate_operation = operands_table.index(line_split[3])
                        for x in range(4, len(line_split)):
                            names_right += [line_split[x].split("[")[0]]
                            formattings_right += [line_split[x][len(names_right[-1]):]]
                    else:
                        raise Exception("Expected 'vec <= vec' or 'vec <= operand vec' at line {} in file {}".format(file_line + 1, filename))
                    
                    if(line_split[0] == "to"):
                        if(not name_left in reference_input_list):
                            raise Exception("Can't assign to a non-input vector at line {} in file {}".format(file_line + 1, filename))
                    else:
                        for name_right in names_right:
                            if(not name_right in reference_output_list):
                                raise Exception("Can't assign from a non-output vector at line {} in file {}".format(file_line + 1, filename))
                        if(vectors_nio_type["{}_{}".format(name_left_prefix, name_left)] == 1):
                            raise Exception("Can't assign to a input vector at line {} in file {}".format(file_line + 1, filename))
                    

                    # check gate types
                    for index_left in positions_left:
                        if(vectors_gate_types["{}_{}".format(name_left_prefix, name_left)][index_left] != -1):
                            raise Exception("Vector range is already assigned at line {} in file {}".format(file_line + 1, filename))
                    
                    # foreach vector on right side
                    for name_right, formatting_right in zip(names_right, formattings_right):
                        ##### check if vector isnt actually a constant, if it is then add this constant to vectors #####
                        if(formatting_right == ""):
                            try:
                                value = int(name_right)
                                if(not "__const_{}_{}".format(name_right, len(positions_left)) in vectors_outputs): # contstant isnt already defined
                                    vectors_outputs["__const_{}_{}".format(name_right, len(positions_left))] = []
                                    vectors_gate_types["__const_{}_{}".format(name_right, len(positions_left))] = []
                                    vectors_nio_type["__const_{}_{}".format(name_right, len(positions_left))] = 0
                                    bf = bitfield(value)[::-1]                                  # generate list of bits from constant
                                    for _ in range(len(positions_left) - len(bf)): bf.append(0) # add items to list if its too small
                                    bf = bf[:len(positions_left)]                               # remove items if its too long
                                    for i in range(len(positions_left)):
                                        vectors_outputs["__const_{}_{}".format(name_right, len(positions_left))] += [[]]
                                        vectors_gate_types["__const_{}_{}".format(name_right, len(positions_left))] += [bf[i]*4] # if its 0 => 0 if its 1 => 4; nand
                                        vectors_outputs["__const_0_1"][0] += [["__const_{}_{}".format(name_right, len(positions_left)), i]]
                                name_right = "_const_{}_{}".format(name_right, len(positions_left))
                            except ValueError:
                                pass
                        # generate absolute positions for vector
                        positions_right = generate_absolute_vector_positions(len(vectors_outputs["{}_{}".format(name_right_prefix, name_right)]), formatting_right)
                        # calculate how many times iterate over vector
                        iterate = max(len(positions_left), len(positions_right))
                        if(len(positions_left) != len(positions_right)):
                            print("Warning: Vectors aren't same size at line {} in file {}".format(file_line + 1, filename))

                        # for connection in left vector and right vector
                        for i in range(iterate):
                            index_left = positions_left[i % len(positions_left)]
                            # Get gate in right vector
                            index_right = positions_right[i % len(positions_right)]
                            # set output gates types
                            vectors_gate_types["{}_{}".format(name_left_prefix, name_left)][index_left] = gate_operation
                            # add gates to input vecotor's outputs
                            vectors_outputs["{}_{}".format(name_right_prefix, name_right)][index_right] += [["{}_{}".format(name_left_prefix, name_left), index_left]]
                else:
                    raise Exception("Expected 'to/exp local_vec <= reference_vec', 'in/out local_vec <= operand reference_vec' at line {} in file {}".format(file_line + 1, filename))

            file_line += 1

        # Export to json file
        output_vector_list = {}
        for vector_name in list(vectors_outputs):
            output_vector_list[vector_name] = [vectors_nio_type[vector_name]]
            output_vector_list[vector_name] += [vectors_outputs[vector_name]]
            if(vectors_nio_type[vector_name] != 1):
                output_vector_list[vector_name] += [vectors_gate_types[vector_name]]
        if(not os.path.exists("build")):
            os.mkdir("build")
        open("build/{}.json".format(os.path.basename(os.path.splitext(filename)[0])), 'wb').write(json.dumps(output_vector_list).encode())
    print("Exported successfully")