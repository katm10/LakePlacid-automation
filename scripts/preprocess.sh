source files.sh

sp=..
op=preprocessed

CFLAGS="-DHAVE_CONFIG_H -I.. -fprofile-arcs -ftest-coverage -DMEMCACHED_DEBUG -g -O2 -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls "

for i in $modules; do
        #echo ~/scratch/mpns_clang/build/bin/clang -E $CFLAGS $sp/$i.c 
        /data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/clang -E $CFLAGS $sp/$i.c > $op/$i.c
done
