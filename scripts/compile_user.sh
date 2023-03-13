source scripts/m.sh

sp=usrc
op=fobjs/src

if [[ $2 != "" ]]; then
	srcs=$2;
fi

for i in $srcs; do
	echo $i
	~/scratch/mpns_clang/build/bin/clang -c -mllvm "--function-table-fname" -mllvm "$1" -I $sp/core -I $sp/event -I $sp/event/modules -I $sp/os/unix -I objs -I $sp/http -I $sp/http/modules $sp/$i.c -o $op/$i.o
done




#cc -c -pipe  -O -W -Wall -Wpointer-arith -Wno-unused-parameter -Werror -g  -I src/core -I src/event -I src/event/modules -I src/os/unix -I objs -I src/http -I src/http/modules
