source files.sh

sp=instrumented
op=instrumented_compiled

CFLAGS=" -g -O2 -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -fPIC"

for i in $modules; do
        /data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/clang -c $CFLAGS $sp/$i.c -o $op/$i.o
       #echo  ~/scratch/mpns_clang/build/bin/clang -c $CFLAGS $sp/$i.c -o $op/$i.o
done
