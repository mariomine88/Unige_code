#include "my_barrier.h"
#include <stdio.h>

unsigned int pthread_my_barrier_init(my_barrier *mb, unsigned int v) {
    if (v == 0) return -1;
    mb->vinit = v;
    mb->val = 0;
    pthread_mutex_init(&mb->lock, NULL);
    pthread_cond_init(&mb->varcond, NULL);
    return 0;
}

unsigned int pthread_my_barrier_wait(my_barrier *mb) {
    pthread_mutex_lock(&mb->lock);
    mb->val++;
    
    if (mb->val < mb->vinit) {
        // Wait until all threads arrive
        while (mb->val < mb->vinit && mb->val > 0) {
            // Wait until either:
            // 1. All threads arrive (val >= vinit), OR
            // 2. Barrier is reset (val == 0)
            pthread_cond_wait(&mb->varcond, &mb->lock);
        }
    } else {
        // Last thread: reset to 0 and wake others
        pthread_cond_broadcast(&mb->varcond);
        mb->val = 0;
    }
    
    pthread_mutex_unlock(&mb->lock);
    return 0;
}

// Test main
static my_barrier mb;

static void* thread_func(void* arg) {
    int id = *(int*)arg;
    printf("Thread %d: before barrier\n", id);
    pthread_my_barrier_wait(&mb);
    printf("Thread %d: after barrier\n", id);
    return NULL;
}

int main() {
    if (pthread_my_barrier_init(&mb, 3) != 0) {
        printf("Barrier init failed\n");
        return -1;
    }

    pthread_t t1, t2, t3;
    int id1 = 1, id2 = 2, id3 = 3;

    pthread_create(&t1, NULL, thread_func, &id1);
    pthread_create(&t2, NULL, thread_func, &id2);
    pthread_create(&t3, NULL, thread_func, &id3);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    pthread_join(t3, NULL);

    return 0;
}