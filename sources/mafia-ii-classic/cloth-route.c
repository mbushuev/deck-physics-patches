#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <unistd.h>

static struct stat clothing;
static int clothing_ready;
#ifdef MAFIA_TRACE_KERNELS
static int trace_kernels;
#endif

__attribute__((constructor)) static void configure(void)
{
    const char *module = getenv("MAFIA_CLOTH_MODULE");
    clothing_ready = module && stat(module, &clothing) == 0;
#ifdef MAFIA_TRACE_KERNELS
    trace_kernels = getenv("MAFIA_CLOTH_KERNEL_PROOF") != NULL;
#endif
}

static void apply_cloth_request(void *memory, size_t size, int protection,
                               int flags, int fd, off_t offset)
{
    static const unsigned char before[] = {0xf6, 0x83, 0x7c, 0x03, 0x00, 0x00, 0x01, 0x74, 0x0d};
    static const unsigned char after[] = {0x80, 0x8b};
    const off_t file_offset = 0x87019;

    if (!clothing_ready || fd < 0 || offset < 0 || offset > file_offset ||
        (uint64_t)(file_offset - offset) + sizeof(before) > size ||
        (flags & MAP_TYPE) != MAP_PRIVATE || !(protection & PROT_READ))
        return;
    struct stat info;
    if (fstat(fd, &info) || info.st_ino != clothing.st_ino || info.st_dev != clothing.st_dev)
        return;
    unsigned char *site = (unsigned char *)memory + (file_offset - offset);
    if (memcmp(site, before, sizeof(before)))
        return;
    const long page_size = sysconf(_SC_PAGESIZE);
    if (page_size <= 0) return;
    void *page = (void *)((uintptr_t)site & ~(uintptr_t)(page_size - 1));
    if (mprotect(page, page_size, (protection | PROT_WRITE) & ~PROT_EXEC))
        return;
    memcpy(site, after, sizeof(after));
    if (mprotect(page, page_size, protection))
        _exit(86);
    static const char message[] = "MAFIA_CLOTH_ROUTE hardware request installed\n";
    (void)write(STDERR_FILENO, message, sizeof(message) - 1);
}

void *mmap(void *address, size_t size, int protection, int flags, int fd, off_t offset)
{
    void *memory = (void *)syscall(SYS_mmap, address, size, protection, flags, fd, offset);
    if (memory != MAP_FAILED) {
        const int saved = errno;
        apply_cloth_request(memory, size, protection, flags, fd, offset);
        errno = saved;
    }
    return memory;
}

void *mmap64(void *address, size_t size, int protection, int flags, int fd, off64_t offset)
{
    return mmap(address, size, protection, flags, fd, offset);
}

#ifdef MAFIA_TRACE_KERNELS
static int (*get_function)(void **, void *, const char *);
static int (*launch_kernel)(void *, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned,
                            unsigned, void *, void **, void **);
static pthread_once_t hip_once = PTHREAD_ONCE_INIT;
static pthread_mutex_t kernel_lock = PTHREAD_MUTEX_INITIALIZER;
static struct { void *function; char name[180]; unsigned calls; } kernels[256];
static unsigned kernel_count;

static void load_hip(void)
{
    void *hip = dlopen("libamdhip64.so.7", RTLD_NOW | RTLD_NOLOAD);
    if (!hip) return;
    get_function = dlsym(hip, "hipModuleGetFunction");
    launch_kernel = dlsym(hip, "hipModuleLaunchKernel");
    dlclose(hip);
}

int hipModuleGetFunction(void **function, void *module, const char *name)
{
    pthread_once(&hip_once, load_hip);
    if (!get_function) return 999;
    const int status = get_function(function, module, name);
    if (trace_kernels && !status && function && *function && name) {
        pthread_mutex_lock(&kernel_lock);
        if (kernel_count < sizeof(kernels)/sizeof(kernels[0])) {
            unsigned i = kernel_count++;
            kernels[i].function = *function;
            snprintf(kernels[i].name, sizeof(kernels[i].name), "%s", name);
            fprintf(stderr, "MAFIA_KERNEL module function=%p name=%s\n", *function, name);
        }
        pthread_mutex_unlock(&kernel_lock);
    }
    return status;
}

int hipModuleLaunchKernel(void *function, unsigned gx, unsigned gy, unsigned gz,
                          unsigned bx, unsigned by, unsigned bz, unsigned shared,
                          void *stream, void **params, void **extra)
{
    pthread_once(&hip_once, load_hip);
    if (!launch_kernel) return 999;
    int status = launch_kernel(function, gx, gy, gz, bx, by, bz, shared, stream, params, extra);
    if (trace_kernels && !status) {
        pthread_mutex_lock(&kernel_lock);
        for (unsigned i = 0; i < kernel_count; ++i) {
            if (kernels[i].function == function) {
                if (++kernels[i].calls == 1 || kernels[i].calls == 128)
                    fprintf(stderr, "MAFIA_KERNEL dispatched count=%u name=%s\n", kernels[i].calls, kernels[i].name);
                break;
            }
        }
        pthread_mutex_unlock(&kernel_lock);
    }
    return status;
}
#endif
