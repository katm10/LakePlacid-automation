source scripts/m.sh

sp=esrc
op=objs/src

if [[ $1 != "" ]]; then
	srcs=$1;
fi

for i in $srcs; do
	echo $i
	~/scratch/mpns_clang/build/bin/clang -c -O -g $sp/$i.c -o $op/$i.o	
done
