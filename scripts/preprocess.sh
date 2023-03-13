source scripts/m.sh

sp=isrc
op=psrc

if [[ $1 != "" ]]; then
	srcs=$1;
fi

for i in $srcs; do
	~/scratch/mpns_clang/build/bin/clang -E -I $sp/core -I $sp/event -I $sp/event/modules -I $sp/os/unix -I objs -I $sp/http -I $sp/http/modules $sp/$i.c > $op/$i.c
done




#cc -c -pipe  -O -W -Wall -Wpointer-arith -Wno-unused-parameter -Werror -g  -I src/core -I src/event -I src/event/modules -I src/os/unix -I objs -I src/http -I src/http/modules
