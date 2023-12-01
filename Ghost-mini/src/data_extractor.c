/*
* Author:   VIVEK DEY (vivek-dey)
*/

// Include necessary libs.
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>


/*
* Func name:        getContainerID
* Parameter(s):     none
* Return type:      char pointer
* Utility:          To get the container ID from the env variable
*                   of the container.
*/
char* getContainerID(){

    char *container_name = getenv("HOSTNAME");

    if(container_name == NULL){
        return NULL;
    }

    return container_name;
}


/*
* Func name:        readProc_stat_file
* Parameter(s):     4: user ->      unsigned long long int pointer
*                      nice ->      unsigned long long int pointer
*                      system ->    unsigned long long int pointer
*                      idle ->      unsigned long long int pointer  
* Return type:      int
* Utility:          To read the first line of /proc/stat file
*                   of the container file system.
*/
int readProc_stat_file(unsigned long long int *user, unsigned long long int *nice,
    unsigned long long int *system, unsigned long long int *idle){

    char buffer[100];
    FILE *procStatFile = fopen("/proc/stat", "r");

    if(procStatFile == NULL){
        return -1;
    }

    fgets(buffer, sizeof(buffer), procStatFile);
    fclose(procStatFile);

    sscanf(buffer, "cpu  %lld %lld %lld %lld", user, nice, system, idle);

    return 0;
}


/*
* Func name:        getContainer_CPU_percentage
* Parameter(s):     none 
* Return type:      float
* Utility:          To call the readProc_stat_file()
                    and calculate the CPU usage percentage.
*/
float getContainer_CPU_percentage(){


    unsigned long long int user_1, nice_1, system_1, idle_1,
                user_2, nice_2, system_2, idle_2;

    readProc_stat_file(&user_1, &nice_1, &system_1, &idle_1);
    sleep(1);
    readProc_stat_file(&user_2, &nice_2, &system_2, &idle_2);

    unsigned long long int total_1 = user_1 + nice_1 + system_1 + idle_1;
    unsigned long long int total_2 = user_2 + nice_2 + system_2 + idle_2;
    long double idle_diff = idle_2 - idle_1;
    long double total_diff = total_2 - total_1;

    float cpuPercentage = (1.0 - (idle_diff / total_diff)) * 100.0;

    return cpuPercentage;
}


/*
* Func name:        readProc_meminfo_file
* Parameter(s):     2:  mem_total ->    long double pointer
                        mem_avail ->    long double pointer
* Return type:      int
* Utility:          To read the values of 'MemTotal' and 'MemAvailable' from /proc/meminfo file
*                   of the container file system.
*/
int readProc_meminfo_file(long double *mem_total, long double *mem_avail){

    char buffer[100];
    FILE *procMeminfoFile = fopen("/proc/meminfo", "r");
    
    if(procMeminfoFile == NULL){
        return -1;
    }

    while(fgets(buffer, sizeof(buffer), procMeminfoFile) != NULL){
        
        if(strncmp(buffer, "MemTotal:", 9) == 0){
            sscanf(buffer + 9, "%Lf", mem_total);
        }
        else if(strncmp(buffer, "MemAvailable:", 13) == 0){
            sscanf(buffer + 13, "%Lf", mem_avail);
        }
    }

    fclose(procMeminfoFile);
 
    return 0;
}


/*
* Func name:        getContainer_memory_percentage
* Parameter(s):     none
* Return type:      float
* Utility:          To call the readProc_meminfo_file()
                    and calculate the memory usage percentage.
*/
float getContainer_memory_percentage(){

    long double mem_total, mem_avail;
    float memPercentage;

    readProc_meminfo_file(&mem_total, &mem_avail);
    memPercentage = (1.0 - (mem_avail / mem_total)) * 100.0;

    return memPercentage;
}