import sys

fname = sys.argv[1]
oname = sys.argv[2]

inf = open(fname, "r")
of = open(oname, "w")

functions = inf.read().strip().split("\n")

of.write("extern void* __user_function_table[1024];\n")

for f in functions:
    of.write("extern void* " + f + "_slow__addr(void);\n")

of.write("void init_user_function_table(void) {\n")

for i in range(len(functions)):
    f = functions[i]
    of.write(
        " " * 4 + "__user_function_table[" + str(i) + "] = " + f + "_slow__addr();\n"
    )

of.write("}")
