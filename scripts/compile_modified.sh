source files.sh

sp=msrc
op=objs/src

if [[ $1 != "" ]]; then
	srcs=$1;
fi

for i in $srcs; do
	echo $i
	/data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/clang -fno-pic -mno-sse -mcmodel=kernel -c -O3 $sp/$i.c -o $op/$i.o	
done
