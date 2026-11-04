#include <stdio.h>
#include <dlfcn.h>
#include "onnxruntime_c_api.h"
int main(int argc,char**argv){if(argc!=2)return 2;void*h=dlopen(argv[1],RTLD_NOW|RTLD_LOCAL);if(!h){fprintf(stderr,"%s\n",dlerror());return 1;}const OrtApiBase*(*get)(void)=dlsym(h,"OrtGetApiBase");if(!get)return 1;const OrtApiBase*b=get();const OrtApi*a=b->GetApi(ORT_API_VERSION);if(!a)return 1;puts(b->GetVersionString());puts(a->GetBuildInfoString());char**p=NULL;int n=0;OrtStatus*s=a->GetAvailableProviders(&p,&n);if(s)return 1;for(int i=0;i<n;i++)puts(p[i]);s=a->ReleaseAvailableProviders(p,n);return s?1:0;}
