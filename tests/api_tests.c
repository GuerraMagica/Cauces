#include "separator.h"
#include <math.h>
#include <stdio.h>
#include <string.h>
static int cancel(double progress,const char* stage,void* user){(void)progress;(void)stage;(void)user;return 0;}
int main(void){
    float source[3]={0,-0.f,0},a[3]={9,9,9},b[3]={9,9,9},r[3]={9,9,9};char error[128];
    if(ds_separate(NULL,source,3,1,48000,a,b,r,NULL,NULL,error,sizeof(error)))return 1;
    if(a[0]!=0||b[1]!=0||!signbit(r[1]))return 2;
    a[0]=9;source[0]=NAN;
    if(!ds_separate(NULL,source,3,1,48000,a,b,r,NULL,NULL,error,sizeof(error))||a[0]!=9||!strlen(error))return 3;
    source[0]=0;
    if(!ds_separate(NULL,source,3,1,48000,a,b,r,cancel,NULL,error,sizeof(error))||a[0]!=9)return 4;
    puts("Public C API contracts passed");return 0;
}
