import read_trace
import sys
import os

def print_manifest(trace):
	print(len(trace["functions"]))
	
	for f in trace["functions"]:
		offsets = []
		if f in trace["branches"]:
			for offset in trace["branches"][f].keys():
				offsets += [offset]
		if len(offsets) > 0:	
			print (f + " " + str(1 + max(offsets)) + " " + str(len(offsets)))
		else:
			print (f + " 0 0")	
		if f in trace["branches"]:
			for offset in trace["branches"][f].keys():
				values = trace["branches"][f][offset]
				choice = 0
				if len(values) > 1:
					choice = 2
				elif len(values) == 1 and values[0] == 0:
					choice = 0
				else:
					choice = 1
				print (str(offset) + " " + str(choice))
					
			

def main():
	if len(sys.argv) < 2:
		print("Usage " + sys.argv[0] + " <filename>")
		exit(1)

	print_manifest(read_trace.read_trace_dir(sys.argv[1]))

if __name__ == "__main__":
	main()
