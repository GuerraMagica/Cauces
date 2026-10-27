// Test-only control; the shipped app contains no networking client.
#include <sys/socket.h>
#include <netinet/in.h>
#include <errno.h>
#include <unistd.h>
#include <stdio.h>
int main(void){
 int fd=socket(AF_INET,SOCK_STREAM,0);if(fd<0){printf("socket_errno=%d\n",errno);return errno==EPERM?0:1;}
 struct sockaddr_in a={0};a.sin_family=AF_INET;a.sin_port=htons(9);a.sin_addr.s_addr=htonl(INADDR_LOOPBACK);
 int result=connect(fd,(const struct sockaddr*)&a,sizeof(a)),code=errno;close(fd);
 printf("connect_result=%d errno=%d\n",result,code);return result==-1&&code==EPERM?0:1;
}
