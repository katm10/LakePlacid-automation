cat $1 | awk '{print "extern int "$1";"}'	

echo "static void * user_global_table[] = {"

cat $1 | awk '{print "(void*)&"$1","}'

echo "};"

echo "void** get_global_table(int* x) {"
echo "    *x = sizeof(user_global_table)/sizeof(*user_global_table);"
echo "    return user_global_table;"
echo "}"
