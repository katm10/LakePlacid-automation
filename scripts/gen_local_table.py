import sys
fname = sys.argv[1]
oname = sys.argv[2]

inf = open(fname, "r")
of = open(oname, "w")

functions = inf.read().strip().split("\n")

of.write("extern void* __local_function_table[1024];\n")

for f in functions:
	of.write("extern void* " + f + "__addr(void);\n")

of.write("void init_local_function_table(void) {\n")

for i in range(len(functions)):
	f = functions[i]
	of.write(" " * 4 + "__local_function_table[" + str(i) + "] = " + f + "__addr();\n")

of.write("}")
