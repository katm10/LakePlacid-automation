source files.sh

sp=preprocessed
op=instrumented


for i in $modules; do
 	/data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/extract-trace $sp/$i.c -- > $op/$i.c
done
