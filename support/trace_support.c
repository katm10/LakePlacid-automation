#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <sys/syscall.h>

pid_t gettid(void) {
	return syscall(SYS_gettid);
}

static int tracing = 0;
static int current_trace = 0;
FILE * current_file;

#define BASEPATH "traces/trace"

int __trace_begin(const char* debugmsg) {
	if (tracing) {
		printf("Warning: traced initialized recursively\n");
		return 0;
	}
	char filename[32] = {0};
	sprintf(filename, "%s%08d.txt", BASEPATH, current_trace);
	current_trace++;
	current_file = fopen(filename, "w");
	if (current_file == NULL) {
		printf("Warning: trace file not opened\n");
		return 0;
	}
	if (debugmsg)
		fprintf(current_file, "%s\n", debugmsg);
	tracing = 1;
	//printf("Begin tracing\n");
}
int __trace_end(void) {
	if (tracing == 0) {
		printf("Warning: trace ended without being started\n");
		return 0;
	}
	if (current_file != NULL) {
		fclose(current_file);
		current_file = NULL;
	}
	tracing = 0;
	
	//printf("End tracing\n");
}
int __trace_condition(const char* name, int offset, int cond) {
	if (tracing) {
		pid_t tid = gettid();
		fprintf(current_file, "[%03d] %32s %08d %d\n", tid, name, offset, cond);
	}
	return cond;
}
int __trace_function(const char* name) {
	if (tracing) {
		pid_t tid = gettid();
		fprintf(current_file, "[%03d] %32s\n", tid, name);
	}
}
int __trace_switch(const char* name, int offset, int val) {
	if (tracing) {
		pid_t tid = gettid();
		fprintf(current_file, "[%03d] %32s %08d %d\n", tid, name, offset, val);
	}
	return val;
}

