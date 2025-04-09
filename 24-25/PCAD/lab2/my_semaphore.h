#include <pthread.h>

typedef struct my_semaphore {
    volatile unsigned int V;
    pthread_mutex_t lock;
    pthread_cond_t varcond;
} my_semaphore;

int my_sem_init(my_semaphore *ms, unsigned int v);
int my_sem_wait(my_semaphore *ms);
int my_sem_signal(my_semaphore *ms);
int my_sem_destroy(my_semaphore *ms);

