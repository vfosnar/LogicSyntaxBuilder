control = {}

# [ctrl, ctrl_index, step, [inst, instt], flag]

inputs = [
    ["ctrl_eip", 1, 0], # EIP -> MI
    ["ctrl_mi",  0, 0],

    ["ctrl_ram", 1, 1], # RAM -> IR
    ["ctrl_ir",  0, 1],
    ["ctrl_eip", 2, 1], # EIP++

    ["ctrl_eip", 1, 2, [0x0C]], # EIP -> MI
    ["ctrl_mi",  0, 2, [0x0C]],
    ["ctrl_ram", 1, 3, [0x0C]], # RAM -> IRR
    ["ctrl_irr", 0, 3, [0x0C]],
    ["ctrl_eip", 2, 3, [0x0C]], # EIP++

    ["ctrl_eip", 1, 2, [0x00]], # EIP -> MI
    ["ctrl_mi",  0, 2, [0x00]],
    ["ctrl_ram", 1, 3, [0x00]], # RAM -> IRR
    ["ctrl_irr", 0, 3, [0x00]],
    ["ctrl_eip", 2, 3, [0x00]], # EIP++
    ["ctrl_eip", 1, 4, [0x00]], # EIP -> MI
    ["ctrl_mi",  0, 4, [0x00]],
    ["ctrl_ram", 1, 5, [0x00]], # RAM -> BUS
    ["ctrl_eip", 2, 5, [0x00]]  # EIP++
]

# EIP -> MI
#
# RAM -> IRR
# EIP++
#
# EIP -> MI
#
# RAM -> ALU_TMP
# EIP++
#
# ALU_TMP << 8 -> ALU_OUT

## EIP -> MI
##
## EIP++
## RAM | ALU_OUT -> ALU_TMP
##
## ALU_TMP << 8 -> ALU_OUT

# ALU_OUT -> MI
#
# RAM -> BUS

for id_ in [0x01, 0x05, 0x09]:
    off = 2
    inputs.append(["ctrl_eip",      1, off, [id_]]) # EIP -> MI
    inputs.append(["ctrl_mi",       0, off, [id_]])
    off += 1#3
    inputs.append(["ctrl_ram",      1, off, [id_]]) # RAM -> IRR
    inputs.append(["ctrl_irr",      0, off, [id_]])
    inputs.append(["ctrl_eip",      2, off, [id_]]) # EIP++
    ##### LOAD PARAMETER #####
    off += 1#4
    inputs.append(["ctrl_eip",      1, off, [id_]]) # EIP -> MI
    inputs.append(["ctrl_mi",       0, off, [id_]])
    off += 1#5
    inputs.append(["ctrl_ram",      1, off, [id_]]) # RAM -> ALU_TMP
    inputs.append(["ctrl_alu_tmp",  0, off, [id_]])
    inputs.append(["ctrl_eip",      2, off, [id_]]) # EIP++
    off += 1#6
    inputs.append(["ctrl_alu",      7, off, [id_]]) # ALU_TMP << 8 -> ALU_OUT
    inputs.append(["ctrl_alu_arch", 2, off, [id_]])
    inputs.append(["ctrl_alu_out",  0, off, [id_]])
    inputs.append(["ctrl_8",        0, off, [id_]])
    # REPEAT
    for x in range(2):
        off += 1#10,7
        inputs.append(["ctrl_eip",      1, off, [id_]]) # EIP -> MI
        inputs.append(["ctrl_mi",       0, off, [id_]])
        off += 1#11,8
        inputs.append(["ctrl_eip",      2, off, [id_]]) # EIP++
        inputs.append(["ctrl_ram",      1, off, [id_]]) # RAM | ALU_OUT -> ALU_TMP
        inputs.append(["ctrl_alu_out",  1, off, [id_]])
        inputs.append(["ctrl_alu_tmp",  0, off, [id_]])
        off += 1#12,9
        inputs.append(["ctrl_alu",      7, off, [id_]]) # ALU_TMP << 8 -> ALU_OUT
        inputs.append(["ctrl_alu_arch", 2, off, [id_]])
        inputs.append(["ctrl_alu_out",  0, off, [id_]])
        inputs.append(["ctrl_8",        0, off, [id_]])
    off += 1#13
    inputs.append(["ctrl_eip",      1, off, [id_]]) # EIP -> MI
    inputs.append(["ctrl_mi",       0, off, [id_]])
    off += 1#14
    inputs.append(["ctrl_eip",      2, off, [id_]]) # EIP++
    inputs.append(["ctrl_ram",      1, off, [id_]]) # RAM | ALU_OUT -> MI
    inputs.append(["ctrl_alu_out",  1, off, [id_]])
    inputs.append(["ctrl_mi",       0, off, [id_]])
    off += 1#15
    inputs.append(["ctrl_ram",     1, off, [id_]]) # RAM -> BUS
print(off)

regs8 = ["al", "ah", "bl", "bh", "cl", "ch", "dl", "dh"]
regs16 = ["ax", "bx", "cx", "dx"]
regs32 = ["eax", "ebx", "ecx", "edx", "esp"]

# INSTRUCTION
#
# all imm/m/r/[r]
# imm   m    r   [r] #
#  00   01   02   03 #
#  04   05   06   07 #
#  08   09   0A   0B #
#
# no preloading
# 0C

id_ = 0
for reg in regs8 + regs16 + regs32:
    off = 4
    inputs.append(["ctrl_{}".format(reg), 0, off, [0x0C, id_]])
    off += 1
    inputs.append(["ctrl_{}".format(reg), 1, off, [0x0C, id_]])
    inputs.append(["sc_rst"             , 0, off, [0x0C, id_]])
    id_ += 1

id_ = 0x99
for reg in regs8:
    off = 5
    inputs.append(["ctrl_{}".format(reg), 0, off, [0x00, id_]])
    off += 1
    inputs.append(["sc_rst"             , 0, off, [0x00, id_]])
    id_ += 1

id_ = 0x99
for reg in regs8: # BYTE MOV [$] $
    off = 15
    inputs.append(["ctrl_{}".format(reg), 0, off, [0x01, id_]])
    off += 1
    inputs.append(["sc_rst"             , 0, off, [0x01, id_]])
    id_ += 1

output_and = {}
output_or = {}

for inp in inputs:
    if(not "{}[{}]".format(inp[0], inp[1]) in output_or):
        output_or["{}[{}]".format(inp[0], inp[1])] = []
    if(len(inp) == 3):
        output_or["{}[{}]".format(inp[0], inp[1])].append("steps[{}]".format(inp[2]))
    elif(len(inp) == 4):
        if(not "cond_{}_{}".format(inp[2], "-".join([str(x) for x in inp[3]])) in output_and):
            output_and["cond_{}_{}".format(inp[2], "-".join([str(x) for x in inp[3]]))] = "steps[{}] {}".format(inp[2], "inst[{}]".format(inp[3][0]) if len(inp[3]) == 1 else "inst[{}] instt[{}]".format(inp[3][0], inp[3][1]))
        output_or["{}[{}]".format(inp[0], inp[1])].append("cond_{}_{}".format(inp[2], "-".join([str(x) for x in inp[3]])))
    elif(len(inp) == 5):
        if(inp[4] >= 0):
            if(not "cond_{}_{}_{}".format(inp[2], "-".join([str(x) for x in inp[3]]), inp[4]) in output_and):
                output_and["cond_{}_{}_{}".format(inp[2], "-".join([str(x) for x in inp[3]]), inp[4])] = "steps[{}] {} flags[{}]".format(inp[2], "inst[{}]".format(inp[3][0]) if len(inp[3]) == 1 else "inst[{}] instt[{}]".format(inp[3][0], inp[3][1]), inp[4])
            output_or["{}[{}]".format(inp[0], inp[1])].append("cond_{}_{}_{}".format(inp[2], "-".join([str(x) for x in inp[3]]), inp[4]))
        else:
            inp[4] = -1 - inp[4]
            if(not "cond_{}_{}_{}".format(inp[2], "-".join([str(x) for x in inp[3]]), inp[4]) in output_and):
                output_and["cond_{}_{}_{}".format(inp[2], "-".join([str(x) for x in inp[3]]), inp[4])] = "steps[{}] {} not_flags[{}]".format(inp[2], "inst[{}]".format(inp[3][0]) if len(inp[3]) == 1 else "inst[{}] instt[{}]".format(inp[3][0], inp[3][1]), inp[4])
            output_or["{}[{}]".format(inp[0], inp[1])].append("cond_{}_{}_{}".format(inp[2], "-".join([str(x) for x in inp[3]]), inp[4]))
if(not "ctrl_eip[0]" in output_or):
    output_or["ctrl_eip[0]"] = []

output_or["ctrl_eip[0]"].append("rst")

define = ""

for and_ in list(output_and):
    define += "{}[1]\n".format(and_)

assign = ""

for and_ in list(output_and):
    assign += "{} <= and {}\n".format(and_, output_and[and_])

for or_ in list(output_or):
    assign += "{} <= or {}\n".format(or_, " ".join(output_or[or_]))

fin = open("main.logic", 'rb').read().decode()

fin = fin.replace(";REPLACEMEDEFINECU", define)
fin = fin.replace(";REPLACEMECU", assign)

open("source/main.logic", 'wb').write(fin.encode())