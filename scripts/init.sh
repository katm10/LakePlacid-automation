source scripts/m.sh

sp=src
op=isrc

for i in $srcs; do
	#~/scratch/mpns_clang/build/bin/clang -E -I $sp/core -I $sp/event -I $sp/event/modules -I $sp/os/unix -I objs -I $sp/http -I $sp/http/modules $sp/$i.c > $op/$i.c
	cp $sp/$i.c $op/$i.c
done
