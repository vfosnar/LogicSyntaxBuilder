define = ""
assign = ""

code = [
    0x00, 0x99, 0x07,
#   BYTE  MOV   DATA
    0x03, 0x99, 0x00, 0x0D, 0x0F
#   BYTE  MOV   REG   HALT  DATA

#    0x01, 0x99, 0x00, 0x00, 0x00, 0x06, 0x69
#   BYTE  MOV   0x00000007
]

for i, value in enumerate(code):
    define += """
sel_{0}_vec[32]
sel_{0}[1]
val_{0}[8]
""".format(i)
    assign += """
sel_{0}_vec <= xor {0} address
@sel_{0} <= nor sel_{0}_vec
@val_{0} <= and sel_{0} {1}
""".format(i, value)

define += """
out out_BUS[32]
bus[8]
in address[32]
in RE[1]
"""

assign += """
@out_BUS[:8] <= and RE bus
bus <= or {}
""".format(" ".join(["val_{0}".format(i) for i in range(len(code))]))

f = open("source/parts/ROM.logic", "w")
f.write("""
define:
{}
assign:
{}
""".format(define, assign))
f.close()