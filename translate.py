import sys
import os
import shlex
import json
import uuid

if __name__ == "__main__":
    if(len(sys.argv) != 3):
        raise Exception("Expected filename and path to export dir (/Scrap/Mechanic/Blueprints/some_uuid/)")
    filename = sys.argv[1]
    path = sys.argv[2]
    
    file = json.loads(open(filename, 'rb').read().decode())

    childs = []
    offset_table = {}

    current_offset = 0
    for vector_name in list(file):
        offset_table[vector_name] = current_offset
        current_offset += len(file[vector_name][1])
    
    current_id = 0
    offset_z = {1:0, 2:0}
    
    for vector_name in list(file):
        for i, gate_outputs in enumerate(file[vector_name][1]):
            gate_type = 0
            if(file[vector_name][0] != 1):
                gate_type = file[vector_name][2][i]
                if(gate_type == -1):
                    gate_type = 0
            
            childs += [{
                "color": "df7f00",
                "controller": {
                    "active": False,
                    "controllers": [{"id":offset_table[output[0]] + output[1]} for output in gate_outputs],
                    "id": current_id,
                    "joints": None,
                    "mode": gate_type
                },
                "pos": {
                    "x": 0,
                    "y": file[vector_name][0],
                    "z": 0 if file[vector_name][0] == 0 else offset_z[file[vector_name][0]]
                },
                "shapeId": "9f0f56e8-2c31-4d83-996c-d00a9b296c3f",
                "xaxis": 2,
                "zaxis": 3
                }]
            current_id += 1
            if(file[vector_name][0] != 0):
                offset_z[file[vector_name][0]] += 1


    # Export
    if(not os.path.exists(path)):
        os.mkdir(path)
        open(os.path.join(path, "description.json"), 'wb').write(json.dumps({
            "description" : "#{STEAM_WORKSHOP_NO_DESCRIPTION}",
            "fileId" : 0,
            "localId" : os.path.split(os.path.dirname(path))[1],
            "name" : "Test BP",
            "type" : "Blueprint",
            "version" : 0
        }).encode())

    open(os.path.join(path, "blueprint.json"), 'wb').write(json.dumps({
        "bodies": [
            {
                "childs": childs
            }
        ],
        "version": 3
    }).encode())

