source scripts/m.sh
sp=psrc
op=locsrc

if [[ $1 != "" ]]; then
	srcs=$1;
fi

for i in $srcs; do
	echo $i
	~/scratch/mpns_clang/build/bin/src-counter $sp/$i.c --extra-arg="-Wno-everything" -- > $op/$i.flist

done
