void *__kernel_function_table[1024] = {0};
void *__user_function_table[1024] = {0};
void *__sorted_kernel_function_table[1024] = {0};
void *__sorted_user_function_table[1024] = {0};

static int kernel_table_init = 0;
static int user_table_init = 0;
static int sorted_table_init = 0;
static int n_functions = 1024;

void init_kernel_function_table(void);
void init_user_function_table(void);

int printf(const char *format, ...);

void populate_kernel_function_table(void) {
  if (kernel_table_init)
    return;
  init_kernel_function_table();
  kernel_table_init = 1;
  return;
}

void populate_user_function_table(void) {
  if (user_table_init)
    return;
  init_user_function_table();
  user_table_init = 1;
  return;
}

void build_sorted_tables() {
  if (sorted_table_init)
    return;

  // Copy over the populated tables
  populate_kernel_function_table();
  populate_user_function_table();

  for (int i = 0; i < 1024; i++) {
    __sorted_kernel_function_table[i] = __kernel_function_table[i];
    __sorted_user_function_table[i] = __user_function_table[i];

    if (__sorted_kernel_function_table[i] == 0) {
      n_functions = i;
      break;
    }
  }

  // Sort the tables
  for (int i = 0; i < 1024; i++) {
    for (int j = i + 1; j < 1024; j++) {
      if (__sorted_kernel_function_table[i] > __sorted_kernel_function_table[j]) {
        void* temp = __sorted_kernel_function_table[i];
        __sorted_kernel_function_table[i] = __sorted_kernel_function_table[j];
        __sorted_kernel_function_table[j] = temp;
      }
      if (__sorted_user_function_table[i] > __sorted_user_function_table[j]) {
        void* temp = __sorted_user_function_table[i];
        __sorted_user_function_table[i] = __sorted_user_function_table[j];
        __sorted_user_function_table[j] = temp;
      }
    }
  }

  sorted_table_init = 1;
}

int is_kernel_function(void* f) {
    build_sorted_tables();

    void* first_kernel_faddr = __sorted_kernel_function_table[0];
    void* first_user_faddr = __sorted_user_function_table[0];

    if (first_kernel_faddr > first_user_faddr) {
        return f >= first_kernel_faddr;
    } else {
        return f < first_user_faddr;
    }
}

int search_user_table(void* f) {
    build_sorted_tables();
    int i = 0;
    while (f > __sorted_user_function_table[i]) {
        i++;
    }
    return i - 1;
}

int search_kernel_table(void* f) {
    build_sorted_tables();
    int i = 0;
    while (f > __sorted_kernel_function_table[i]) {
        i++;
    }
    return i - 1;
}

void* __translate_function_(void* f, int switch_ctx) {
    populate_user_function_table();
    populate_kernel_function_table();

    if (!kernel_table_init) {
        printf("kernel Function Table not initialized");
        return 0;
    }
    char* faddr = (char*) f;
    faddr -= 12;
    int context = *((int*) faddr);
    faddr -= 4;
    int index = *((int*) faddr);

    // assume we want to go to the user context for now
    int new_ctx = (switch_ctx) ? !context : context;
    printf("Current context: %d\nSwitching? %d\nNew context: %d\n", context, switch_ctx, new_ctx);
    if (new_ctx) {
        // printf("Returning user function %p\n\n", __user_function_table[index]);
        return __user_function_table[index];
    } else {
        // printf("Returning kernel function %p\n\n", __kernel_function_table[index]);
        return __kernel_function_table[index];
    }
}

void* __translate_function(void* f) {
    return __translate_function_(f, 0);
}

void* mpns_abort(void *fn, void *rip) {
    char* faddr = (char*) fn;
    faddr -= 12;
    int context = *((int*) faddr);

    if (context == 1) {
      // in userspace, just keep going
      return rip;
    }

    void *new_fxn = __translate_function_(fn, 1);

    return new_fxn + (rip - fn);
}

void* translate_return_addr(void *old_eip) {
    // This should only get called from the user version
    // printf("Translating return address %p\n", old_eip);
    
    if (is_kernel_function(old_eip)) {
        // Check if this is the dispatch function 
        int indx = search_kernel_table(old_eip);
        printf("Kernel function index: %d\n", indx);

        // TODO make this better lol, whatta hack
        if (indx == 4) {
            printf("Returning back to kernel dispatch\n");
            return old_eip;
        }
        // Convert this to a user function
        printf("Converting return to user addr\n");
        void* new_fxn_start = __sorted_user_function_table[indx];
        return new_fxn_start + (old_eip - __sorted_kernel_function_table[indx]);
    }
    return old_eip;
}