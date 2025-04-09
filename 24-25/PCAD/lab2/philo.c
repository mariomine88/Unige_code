#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "my_semaphore.c"

#define NUM_PHILOSOPHERS 5
#define EAT_TIMES 5

// Chopsticks represented as semaphores
my_semaphore chopsticks[NUM_PHILOSOPHERS];

void* philosopher(void* arg) {
    int id = *(int*)arg;
    int left = id;
    int right = (id + 1) % NUM_PHILOSOPHERS;

    for (int i = 0; i < EAT_TIMES; i++) {
        printf("Filosofo %d: sta pensando\n", id);
        sleep(1);

        my_sem_wait(&chopsticks[left]);
        printf("Filosofo %d: ha la sua bacchetta sinistra\n", id);
        my_sem_wait(&chopsticks[right]);
        printf("Filosofo %d: ha la sua bacchetta destra\n", id);

        printf("Filosofo %d: sta mangiando\n", id);
        sleep(1);

        my_sem_signal(&chopsticks[left]);
        my_sem_signal(&chopsticks[right]);
        printf("Filosofo %d: ha rilasciato le sue due bacchette\n", id);
    }
    return NULL;
}

int main() {
    pthread_t philosophers[NUM_PHILOSOPHERS];
    int ids[NUM_PHILOSOPHERS];

    // Initialize semaphores with value 1 (available)
    for (int i = 0; i < NUM_PHILOSOPHERS; i++) {
        my_sem_init(&chopsticks[i], 1);
        ids[i] = i;
    }

    for (int i = 0; i < NUM_PHILOSOPHERS; i++) {
        pthread_create(&philosophers[i], NULL, philosopher, &ids[i]);
    }

    for (int i = 0; i < NUM_PHILOSOPHERS; i++) {
        pthread_join(philosophers[i], NULL);
    }

    // Clean up semaphores
    for (int i = 0; i < NUM_PHILOSOPHERS; i++) {
        my_sem_destroy(&chopsticks[i]);
    }

    return 0;
}