source scripts/m.sh
sp=psrc
op=esrc
if [[ $1 != "" ]]; then
	srcs=$1;
fi

for i in $srcs; do
	echo $i
	~/scratch/mpns_clang/build/bin/extract-trace $sp/$i.c -- > $op/$i.c
done
