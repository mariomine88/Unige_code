#include <pthread.h>

typedef struct my_barrier {
    volatile unsigned int vinit;
    volatile unsigned int val;
    pthread_mutex_t lock;
    pthread_cond_t varcond;
} my_barrier;

unsigned int pthread_my_barrier_init(my_barrier *mb, unsigned int v);
unsigned int pthread_my_barrier_wait(my_barrier *mb);