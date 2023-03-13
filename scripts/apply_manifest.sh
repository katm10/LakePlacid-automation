source files.sh
sp=preprocessed
op=msrc

rm -rf $op
mkdir $op

if [[ $2 != "" ]]; then
	srcs=$2;
fi

for i in $srcs; do
	echo $i
	/data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/apply-manifest ../$i.c $1 $sp/$i.c -- > $op/$i.1.c
	/data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/patch-globals ../$i.c $op/$i.1.c --extra-arg="-Wno-everything" -- > $op/$i.2.c
	/data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/patch-functions ../$i.c $op/$i.2.c --extra-arg="-Wno-everything" -- > $op/$i.c
#	echo /data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/apply-manifest $1 $sp/$i.c --extra-arg="-Wno-everything" -- to $op/$i.1.c
#	echo /data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/patch-globals $op/$i.1.c --extra-arg="-Wno-everything" -- to $op/$i.2.c
#	echo /data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/patch-functions $op/$i.2.c --extra-arg="-Wno-everything" -- to $op/$i.c
done
