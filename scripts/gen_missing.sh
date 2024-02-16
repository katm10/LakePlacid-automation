echo "void mpns_abort(const char*, int);"
cat $1 | awk '{print "void "$1"(){mpns_abort(\""$1"\", -1);}"}'	
