/*
* Author:   VIVEK DEY (vivek-dey)
*/

// Include necessary libs and other defined modules.
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <signal.h>
#include <string.h>
#include "data_extractor.h"
#include "network_manager.h"


/*
* Func name:        daemonize
* Parameter(s):     none
* Return type:      void
* Utility:          To make 'mini-ghost' a background running process(a daemon)
                    and detach it from the container's shell.
*/
void daemonize(){
    
    sleep(40);

    pid_t pid, sid;
    pid = fork();

    if(pid < 0){
        exit(1);
    }
    if(pid > 0){
        exit(0);
    }

    umask(0);

    sid = setsid();
    if(sid < 0){
        exit(1);
    }

    if((chdir("/")) < 0){
        exit(1);
    }

    close(STDIN_FILENO);
    close(STDOUT_FILENO);
    close(STDERR_FILENO);

    signal(SIGTERM, exit);
}


// 'The MAIN' as we all know!
int main(){

    char data[30] = {0};

    initNetworkModule();

    char *containerID = getContainerID();
    float CPUpercentage, memoryPercentage;

    daemonize();

    int exit = 0;
    while(!exit){
        
        CPUpercentage = getContainer_CPU_percentage();
        memoryPercentage = getContainer_memory_percentage();

        snprintf(data, sizeof(data), "%s %.2f %.2f", containerID, CPUpercentage, memoryPercentage);
        sendData(data, 0);

        memset(data, '\0', sizeof(data));

        if(strcmp(readData(), "x") == 0){
            
            snprintf(data, sizeof(data), "%s %s", containerID, "| mini > (x_x)");
            sendData(data, 1);
            exit = 1;
        }
    }
    
    return 0;
}