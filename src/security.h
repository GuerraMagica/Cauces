#pragma once
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif
// Handles pin the parent and owned directory. Destroy never follows replacement paths.
typedef struct cauces_directory cauces_directory;
cauces_directory* cauces_directory_create(const char* parent, const char* prefix, char* error, size_t capacity);
cauces_directory* cauces_directory_adopt(const char* path, char* error, size_t capacity);
const char* cauces_directory_path(const cauces_directory* directory);
int cauces_directory_copy(cauces_directory* directory, const char* source, const char* name, char* error, size_t capacity);
int cauces_directory_publish(cauces_directory* directory, const char* name, char* error, size_t capacity);
void cauces_directory_cancel(cauces_directory* directory);
void cauces_directory_destroy(cauces_directory* directory);
#ifdef __cplusplus
}
#endif
