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
        pthread_cond_wait(&mb->varcond, &mb->lock);
    } else {
        // Last thread: reset to 0 and wake others
        mb->val = 0;
        pthread_cond_broadcast(&mb->varcond);
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
    // Test with 5, 10, 15, 20 threads
    for (int thread_count = 5; thread_count <= 20; thread_count += 5) {
        printf("Testing with %d threads\n", thread_count);
        if (pthread_my_barrier_init(&mb, thread_count) != 0) {
            printf("Barrier init failed\n");
            return -1;
        }

        pthread_t threads[thread_count];
        int ids[thread_count];

        for (int i = 0; i < thread_count; i++) {
            ids[i] = i + 1;
            pthread_create(&threads[i], NULL, thread_func, &ids[i]);
        }

        for (int i = 0; i < thread_count; i++) {
            pthread_join(threads[i], NULL);
        }

        printf("\n");
        printf("Barrier test completed\n\n");
    }

    return 0;
}