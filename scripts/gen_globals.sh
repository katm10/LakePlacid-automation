echo "extern void* __globals_table[1024];"
cat $1 | awk '{print "void* "$1"__addr(){return __globals_table["NR-1"];}"}'	
