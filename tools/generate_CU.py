control = {}


#       0x00  0x01  0x02  0x03  0x04  0x05  0x06  0x07
regs8 = ["al", "ah", "bl", "bh", "cl", "ch", "dl", "dh"]
#        0x08  0x09  0x0A  0x0B
regs16 = ["ax", "bx", "cx", "dx"]
#         0x0C   0x0D   0x0E   0x0F   0x10
regs32 = ["eax", "ebx", "ecx", "edx", "esp"]

regId = {i:reg for i, reg in enumerate(regs8 + regs16 + regs32)}


# [ctrl, ctrl_index, step, [inst, instt], flag]

inputs = [
    ["ctrl_eip", 1, 0], # EIP -> MI
    ["ctrl_mi",  0, 0],

    ["ctrl_ram", 1, 1], # RAM -> IR
    ["ctrl_ir",  0, 1],
    ["ctrl_eip", 2, 1], # EIP++
]

# PRELOAD BYTE

for id_ in [0x00, 0x04, 0x08]:
    off = 2
    inputs.append(["ctrl_eip", 1, off, [id_]]) # EIP -> MI
    inputs.append(["ctrl_mi",  0, off, [id_]])
    off += 1 # 3
    inputs.append(["ctrl_ram", 1, off, [id_]]) # RAM -> IRR
    inputs.append(["ctrl_irr", 0, off, [id_]])
    inputs.append(["ctrl_eip", 2, off, [id_]]) # EIP++
    ##### LOAD PARAMETER #####
    off += 1 # 4
    inputs.append(["ctrl_eip", 1, off, [id_]]) # EIP -> MI
    inputs.append(["ctrl_mi",  0, off, [id_]])
    off += 1 # 5
    inputs.append(["ctrl_ram", 1, off, [id_]]) # RAM -> BUS
    inputs.append(["ctrl_eip", 2, off, [id_]]) # EIP++
    print("{}: {}".format(hex(id_), off))

# PRELOAD BYTE FROM ADDRESS

for id_ in [0x01, 0x05, 0x09]:
    off = 2
    inputs.append(["ctrl_eip",      1, off, [id_]]) # EIP -> MI
    inputs.append(["ctrl_mi",       0, off, [id_]])
    off += 1 # 3
    inputs.append(["ctrl_ram",      1, off, [id_]]) # RAM -> IRR
    inputs.append(["ctrl_irr",      0, off, [id_]])
    inputs.append(["ctrl_eip",      2, off, [id_]]) # EIP++
    ##### LOAD PARAMETER #####
    off += 1 # 4
    inputs.append(["ctrl_eip",      1, off, [id_]]) # EIP -> MI
    inputs.append(["ctrl_mi",       0, off, [id_]])
    off += 1 # 5
    inputs.append(["ctrl_ram",      1, off, [id_]]) # RAM -> ALU_TMP
    inputs.append(["ctrl_alu_tmp",  0, off, [id_]])
    inputs.append(["ctrl_eip",      2, off, [id_]]) # EIP++
    off += 1 # 6
    inputs.append(["ctrl_alu",      7, off, [id_]]) # ALU_TMP << 8 -> ALU_OUT
    inputs.append(["ctrl_alu_arch", 2, off, [id_]])
    inputs.append(["ctrl_alu_out",  0, off, [id_]])
    inputs.append(["ctrl_8",        0, off, [id_]])
    # REPEAT
    for x in range(2):
        off += 1 # 7, 10
        inputs.append(["ctrl_eip",      1, off, [id_]]) # EIP -> MI
        inputs.append(["ctrl_mi",       0, off, [id_]])
        off += 1 # 8, 11
        inputs.append(["ctrl_eip",      2, off, [id_]]) # EIP++
        inputs.append(["ctrl_ram",      1, off, [id_]]) # RAM | ALU_OUT -> ALU_TMP
        inputs.append(["ctrl_alu_out",  1, off, [id_]])
        inputs.append(["ctrl_alu_tmp",  0, off, [id_]])
        off += 1 # 9, 12
        inputs.append(["ctrl_alu",      7, off, [id_]]) # ALU_TMP << 8 -> ALU_OUT
        inputs.append(["ctrl_alu_arch", 2, off, [id_]])
        inputs.append(["ctrl_alu_out",  0, off, [id_]])
        inputs.append(["ctrl_8",        0, off, [id_]])
    off += 1 # 13
    inputs.append(["ctrl_eip",      1, off, [id_]]) # EIP -> MI
    inputs.append(["ctrl_mi",       0, off, [id_]])
    off += 1 # 14
    inputs.append(["ctrl_eip",      2, off, [id_]]) # EIP++
    inputs.append(["ctrl_ram",      1, off, [id_]]) # RAM | ALU_OUT -> MI
    inputs.append(["ctrl_alu_out",  1, off, [id_]])
    inputs.append(["ctrl_mi",       0, off, [id_]])
    off += 1 # 15
    inputs.append(["ctrl_ram",     1, off, [id_]]) # RAM -> BUS
    print("{}: {}".format(hex(id_), off))

# PRELOAD BYTE FROM REGISTER


# NO PRELOADING
off = 2
inputs.append(["ctrl_eip", 1, 2, [0x0C]]) # EIP -> MI
inputs.append(["ctrl_mi",  0, 2, [0x0C]])
off += 1
inputs.append(["ctrl_ram", 1, 3, [0x0C]]) # RAM -> IRR
inputs.append(["ctrl_irr", 0, 3, [0x0C]])
inputs.append(["ctrl_eip", 2, 3, [0x0C]]) # EIP++

# INSTRUCTION
## with value preload
#
# all imm/m/r/[r]
# imm   m    r   [r]
#  00   01   02   03  byte
#  04   05   06   07  word
#  08   09   0A   0B  long
#
# instructions
# 00 ADD
# 11 SUB
# 22 OR
# 33 XOR
# 44 ROL
# 55 ROR
# 66 SHL
# 77 SHR
# 88 CMP
# 99 MOV
# AA MOVM
# BB CALL
# CC POP
# DD PUSH
#
## without value preload
#
# 0C
#
# instructions
# 00 RST
# 11 INC
# 22 DEC
# 33 NOT

# PRELOAD INDICATOR -> ir
# INSTRUCTION -> irr
# execute preload
# execute instruction

id_ = 0
for reg in regs8 + regs16 + regs32:
    off = 4
    inputs.append(["ctrl_{}".format(reg), 0, off, [0x0C, id_]])
    off += 1
    inputs.append(["ctrl_{}".format(reg), 1, off, [0x0C, id_]])
    inputs.append(["sc_rst"             , 0, off, [0x0C, id_]])
    id_ += 1

id_ = 0x99
for reg in regs8: # BYTE MOV $
    off = 5
    inputs.append(["ctrl_{}".format(reg), 0, off, [0x00, id_]])
    off += 1
    inputs.append(["sc_rst"             , 0, off, [0x00, id_]])
    id_ += 1

id_ = 0x99
for reg in regs8: # BYTE MOV [$]
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