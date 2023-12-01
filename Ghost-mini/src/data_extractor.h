char* getContainerID();

int readProc_stat_file(unsigned long long int*, unsigned long long int*,
    unsigned long long int*, unsigned long long int*);

float getContainer_CPU_percentage();

int readProc_meminfo_file(long double*, long double*);

float getContainer_memory_percentage();