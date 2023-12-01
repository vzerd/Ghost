/*
* Author:   VIVEK DEY (vivek-dey)
*/

// Include necessary libs.
#include <arpa/inet.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

// Define the 'ghost-node' port number.
#define PORT 9876

// Define socket variables.
int status, miniSockt;
struct sockaddr_in serv_addr;

// Define buffer to store IP address of 'ghost-node'.
char IPbuffer[15] = {0};
// Define buffer to store 'read data' from 'ghost-node'.
char recvBuffer[5] = {0};


/*
* Func name:        getIPfromDNS
* Parameter(s):     none
* Return type:      void
* Utility:          To perform a local DNS lookup and get 
*                   the IP address assigned to 'ghost-node'.
*/
void getIPfromDNS(){

    char tempBuffer[16];
    FILE *cmdResponse;
    cmdResponse = popen("sh -c 'nslookup ghost-node | grep -oE \"\\b172\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\b\"'", "r");

    fgets(tempBuffer, sizeof(tempBuffer), cmdResponse);

    for(int i = 0; tempBuffer[i] != '\n'; i++){
        IPbuffer[i] = tempBuffer[i];
    }

    pclose(cmdResponse);
}


/*
* Func name:        initNetworkModule
* Parameter(s):     none
* Return type:      int
* Utility:          To initialize/configure the socket for communication.
*/
int initNetworkModule(){

    getIPfromDNS();

    if((miniSockt = socket(AF_INET, SOCK_STREAM, 0)) < 0){
		return -1;
	}

    serv_addr.sin_family = AF_INET;
	serv_addr.sin_port = htons(PORT);

    if(inet_pton(AF_INET, IPbuffer, &serv_addr.sin_addr) <= 0){
        return -1;
	}

    if((status	= connect(miniSockt, (struct sockaddr*)&serv_addr, sizeof(serv_addr))) < 0){
        return -1;
	}

    return 0;
}


/*
* Func name:        sendData
* Parameter(s):     1:  data ->     char pointer
* Return type:      int
* Utility:          To send 'data' passed in as parameter, to 'ghost-node'.
*/
int sendData(char *data, int socCloseStts){

    send(miniSockt, data, strlen(data), 0);

    if(socCloseStts){
        close(miniSockt);
    }
	
    return 0;
}


/*
* Func name:        readData
* Parameter(s):     none
* Return type:      char
* Utility:          To read data from 'ghost-node'.
*/
char* readData(){

    read(miniSockt, recvBuffer, sizeof(recvBuffer));

    return recvBuffer;
}