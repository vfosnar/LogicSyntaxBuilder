control = {}

# [ctrl, ctrl_index, step, inst, flag]

inputs = [
    ["ctrl_eip", 1, 0],
    ["ctrl_mi", 0, 0],

    ["ctrl_ram", 1, 1],
    ["ctrl_ir", 0, 1],
    ["ctrl_eip", 2, 1]
]

regs8 = ["al", "ah", "bl", "bh", "cl", "ch", "dl", "dh"]
regs16 = ["ax", "bx", "cx", "dx"]
regs32 = ["eax", "ebx", "ecx", "edx", "esp", "eip"]

#  0 - 18 | RST
# 18 - 36 | INC
# 36 - 54 | DEC

id_ = 0
for reg in regs8 + regs16 + regs32:
    inputs.append(["ctrl_{}".format(reg), 0, 2, id_])
    inputs.append(["sc_rst", 0, 3, id_])
    id_ += 1

for reg in regs8 + regs16 + regs32:
    inputs.append(["ctrl_{}".format(reg), 2, 2, id_])
    inputs.append(["ctrl_eax", 1, 3, id_])
    inputs.append(["sc_rst", 0, 3, id_])
    id_ += 1

for reg in regs8 + regs16 + regs32:
    inputs.append(["ctrl_{}".format(reg), 3, 2, id_])
    inputs.append(["ctrl_eax", 1, 3, id_])
    inputs.append(["sc_rst", 0, 3, id_])
    id_ += 1

output_and = {}
output_or = {}

for inp in inputs:
    if(not "{}[{}]".format(inp[0], inp[1]) in output_or):
        output_or["{}[{}]".format(inp[0], inp[1])] = []
    if(len(inp) == 3):
        output_or["{}[{}]".format(inp[0], inp[1])].append("steps[{}]".format(inp[2]))
    elif(len(inp) == 4):
        if(not "cond_{}_{}".format(inp[2], inp[3]) in output_and):
            output_and["cond_{}_{}".format(inp[2], inp[3])] = "steps[{}] inst[{}]".format(inp[2], inp[3])
        output_or["{}[{}]".format(inp[0], inp[1])].append("cond_{}_{}".format(inp[2], inp[3]))
    elif(len(inp) == 5):
        if(inp[4] >= 0):
            if(not "cond_{}_{}_{}".format(inp[2], inp[3], inp[4]) in output_and):
                output_and["cond_{}_{}_{}".format(inp[2], inp[3], inp[4])] = "steps[{}] inst[{}] flags[{}]".format(inp[2], inp[3], inp[4])
            output_or["{}[{}]".format(inp[0], inp[1])].append("cond_{}_{}_{}".format(inp[2], inp[3], inp[4]))
        else:
            inp[4] = -1 - inp[4]
            if(not "cond_{}_{}_{}".format(inp[2], inp[3], inp[4]) in output_and):
                output_and["cond_{}_{}_{}".format(inp[2], inp[3], inp[4])] = "steps[{}] inst[{}] not_flags[{}]".format(inp[2], inp[3], inp[4])
            output_or["{}[{}]".format(inp[0], inp[1])].append("cond_{}_{}_{}".format(inp[2], inp[3], inp[4]))
if(not "ctrl_eip[0]" in output_or):
    output_or["ctrl_eip[0]"] = []

output_or["ctrl_eip[0]"].append("rst")

print("\nDefine:\n")

for and_ in list(output_and):
    print("{}[1]".format(and_))

print("\nAssign:\n")

for and_ in list(output_and):
    print("{} <= and {}".format(and_, output_and[and_]))

for or_ in list(output_or):
    print("{} <= or {}".format(or_, " ".join(output_or[or_])))