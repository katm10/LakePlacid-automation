import os
import sys
import os.path


def read_trace_dir(dirname):
	trace = {}
	for fname in os.listdir(dirname):
		fname = dirname + "/" + fname
		if os.path.isfile(fname):
			trace = read_trace(fname, trace)
	return trace		

def read_trace(fname, trace = {}):
	tf = open(fname, "r")
	command = tf.readline().strip()	

	trace["command"] = command

	if "functions" not in trace.keys():
		trace["functions"] = []
	if "branches" not in trace.keys():
		trace["branches"] = {}

	for line in tf:
		line = line.strip()	
		tokens = line.split()

		if len(tokens) == 2:
			fname = tokens[1].strip()
			if fname not in trace["functions"]:
				trace["functions"].append(fname)
		else:
			fname = tokens[1].strip()
			offset = int(tokens[2].strip())
			val = int(tokens[3].strip())	
			if fname not in trace["branches"].keys():
				trace["branches"][fname] = {}
			if offset not in trace["branches"][fname].keys():
				trace["branches"][fname][offset] = []
			if val not in trace["branches"][fname][offset]:
				trace["branches"][fname][offset].append(val)

	return trace	

def main():
	if len(sys.argv) < 2:
		print("Usage " + sys.argv[0] + " <filename>")
		exit(1)

	print(read_trace(sys.argv[1]))


if __name__ == "__main__":
	main()
