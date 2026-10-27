#ifndef DIALOGUE_SEPARATOR_H
#define DIALOGUE_SEPARATOR_H
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif
typedef struct ds_context ds_context;
/* Return zero to cancel. Called synchronously on the processing thread. */
typedef int (*ds_progress)(double fraction,const char* stage,void* user);
/* Models and runtime must be local. Returns NULL and a UTF-8 diagnostic on error. */
ds_context* ds_create(const char* models_directory,int threads,char* error,size_t error_capacity);
void ds_destroy(ds_context* context);
/* Float32 planar input/output, [channels,frames], mono or identical dual mono.
   Output buffers must each hold frames*channels samples and not overlap.
   No I/O. A NULL context supports silence only. Outputs unchanged on failure.
   Returns 0 on success, 1 on failure; diagnostic is NUL-terminated when capacity>0.
   A context is single-threaded: do not call/destroy it concurrently. */
int ds_separate(ds_context* context,const float* input,size_t frames,int channels,int sample_rate,
                float* speaker_1,float* speaker_2,float* residual,ds_progress progress,void* user,
                char* error,size_t error_capacity);
#ifdef __cplusplus
}
#endif
#endif
