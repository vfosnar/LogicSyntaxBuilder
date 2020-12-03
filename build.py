import sys
import os
import shlex
import json

if __name__ == "__main__":
    #if(len(sys.argv) != 2):
    #    raise Exception("Invalid parameter count")
    vectors_outputs = {} # {"a":[["b", 0]]}
    vectors_gate_types = {}

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
            if(line == "define:"):
                stage = 2
            line_split = shlex.split(line)
            if(line_split[0] == "use"):
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

                ##### Frickin finally load reference #####
                for vector_name in list(reference_json_data):
                    if(reference_json_data[vector_name][0] in [0, 2]):
                        # when vector is normal or output

                        # define local vectors
                        vectors_outputs["{}_{}".format(reference_prefix, vector_name)] = []
                        vectors_gate_types["{}_{}".format(reference_prefix, vector_name)] = []

                        # for each gate in vector
                        for reference_vector_outputs, gate_type in zip(reference_json_data[vector_name][1], reference_json_data[vector_name][2]):
                            # add gate to vector
                            vectors_outputs["{}_{}".format(reference_prefix, vector_name)] += [[]]
                            # add gate type to gate type vector
                            vectors_gate_types["{}_{}".format(reference_prefix, vector_name)] += [gate_type]

                            # for each connection from this gate
                            for reference_vector_output in reference_vector_outputs:
                                # Just set prefix and add connection under gate to local vector ex. ["a", 0] -> ["a_0", 0]
                                vectors_outputs["{}_{}".format(reference_prefix, vector_name)][-1] += [["{}_{}".format(reference_prefix, reference_vector_output[0]), reference_vector_output[1]]]
                    elif(reference_json_data[vector_name][0] == 1):
                        # when vector is input
                        # inputs cant have defined gate types becouse gate type changes when referenced and assigned

                        # define local vector
                        vectors_outputs["{}_{}".format(reference_prefix, vector_name)] = []
                        # for each gate in vector
                        for reference_vector_outputs in reference_json_data[vector_name][1]:
                            # add gate to vector
                            vectors_outputs["{}_{}".format(reference_prefix, vector_name)] += [[]]

                            # for each connection from this gate
                            for reference_vector_output in reference_vector_outputs:
                                # Just set prefix and add connection under gate to local vector ex. ["a", 0] -> ["a_0", 0]
                                vectors_outputs["{}_{}".format(reference_prefix, vector_name)][-1] += [["{}_{}".format(reference_prefix, reference_vector_output[0]), reference_vector_output[1]]]
                    else:
                        raise Exception("Unknown connection type when parsing json file at line {}".format(file_line))
            
            else:
                raise Exception("Unexpected symbol at line {}".format(file_line))
        
        elif(stage == 2):
            pass
                
        file_line += 1