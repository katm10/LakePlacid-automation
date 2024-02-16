gcc -c -mcmodel=kernel -fno-pic missing.c
gcc -c -mcmodel=kernel -fno-pic globals.c
gcc -c globals_user.c
gcc -c -mcmodel=kernel -fno-pic local_table.c
