source files.sh

sp=preprocessed
op=instrumented


for i in $modules; do
 	compilers/extract_trace $sp/$i.c -- > $op/$i.c
done
