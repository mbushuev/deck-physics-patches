#define _GNU_SOURCE
#include <dlfcn.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

enum { HIP_SUCCESS = 0, HIP_MEMORY_DEVICE = 2, HIP_ERROR_UNKNOWN = 999 };
/* ABI of hipPointerAttribute_t in HIP 7.2. */
struct hip_pointer_attributes {
    int type;
    int device;
    void *device_pointer;
    void *host_pointer;
    int is_managed;
    unsigned allocation_flags;
};

static int (*original_fill)(void *, unsigned char, size_t);
static int (*queued_fill)(void *, unsigned char, size_t, void *);
static int (*pointer_attributes)(struct hip_pointer_attributes *, const void *);
static const char *log_path;
static atomic_uint applied;
static atomic_uint bypassed;
static atomic_uint async_errors;
static pthread_once_t bind_once = PTHREAD_ONCE_INIT;

static void bind_hip(void) {
    void *hip = dlopen("libamdhip64.so.7", RTLD_NOW | RTLD_NOLOAD);
    if (!hip)
        return;
    original_fill = dlsym(hip, "hipMemsetD8");
    queued_fill = dlsym(hip, "hipMemsetD8Async");
    pointer_attributes = dlsym(hip, "hipPointerGetAttributes");
    log_path = getenv("MAFIA_GPU_FILL_LOG");
}

unsigned mafia_async_fill_hits(void) {
    return atomic_load_explicit(&applied, memory_order_relaxed);
}
unsigned mafia_async_fill_bypasses(void) {
    return atomic_load_explicit(&bypassed, memory_order_relaxed);
}

static void record_counts(void) {
    if (!log_path)
        return;
    FILE *file = fopen(log_path, "a");
    if (!file)
        return;
    fprintf(file, "%u %u %u\n", mafia_async_fill_hits(), mafia_async_fill_bypasses(),
            atomic_load_explicit(&async_errors, memory_order_relaxed));
    fclose(file);
}

int hipMemsetD8(void *ptr, unsigned char value, size_t bytes) {
    pthread_once(&bind_once, bind_hip);
    if (!original_fill)
        return HIP_ERROR_UNKNOWN;
    if (!ptr || value != 0xff || bytes != 0x20000 || !queued_fill || !pointer_attributes)
        return original_fill(ptr, value, bytes);

    struct hip_pointer_attributes attr = {0};
    if (pointer_attributes(&attr, ptr) != HIP_SUCCESS || attr.type != HIP_MEMORY_DEVICE ||
        attr.is_managed || attr.host_pointer) {
        atomic_fetch_add_explicit(&bypassed, 1, memory_order_relaxed);
        return original_fill(ptr, value, bytes);
    }

    /* Keep the HIP legacy default stream used by the synchronous entry point. */
    int result = queued_fill(ptr, value, bytes, NULL);
    if (result != HIP_SUCCESS) {
        atomic_fetch_add_explicit(&async_errors, 1, memory_order_relaxed);
        record_counts();
        return result;
    }
    unsigned hits = atomic_fetch_add_explicit(&applied, 1, memory_order_relaxed) + 1;
    if (hits == 1 || (hits & 255u) == 0)
        record_counts();
    return result;
}
