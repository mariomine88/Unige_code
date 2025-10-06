#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

#define NUM_PHILOSOPHERS 5
#define EAT_TIMES 5

pthread_mutex_t chopsticks[NUM_PHILOSOPHERS];

void* philosopher(void* arg) {
    int id = *(int*)arg;
    int left = id;
    int right = (id + 1) % NUM_PHILOSOPHERS;

    for (int i = 0; i < EAT_TIMES; i++) {
        printf("Filosofo %d: sta pensando\n", id);
        sleep(1);

        pthread_mutex_lock(&chopsticks[left]);
        printf("Filosofo %d: ha la sua bacchetta sinistra\n", id);
        sleep(1);

        pthread_mutex_lock(&chopsticks[right]);
        printf("Filosofo %d: ha la sua bacchetta destra\n", id);

        printf("Filosofo %d: sta mangiando\n", id);
        sleep(1);

        pthread_mutex_unlock(&chopsticks[left]);
        pthread_mutex_unlock(&chopsticks[right]);
        printf("Filosofo %d: ha rilasciato le sue due bacchette\n", id);
    }
}

int main() {
    pthread_t philosophers[NUM_PHILOSOPHERS];
    int ids[NUM_PHILOSOPHERS];

    for (int i = 0; i < NUM_PHILOSOPHERS; i++) {
        pthread_mutex_init(&chopsticks[i], NULL);
        ids[i] = i;
    }

    for (int i = 0; i < NUM_PHILOSOPHERS; i++) {
        pthread_create(&philosophers[i], NULL, philosopher, &ids[i]);
    }

    for (int i = 0; i < NUM_PHILOSOPHERS; i++) {
        pthread_join(philosophers[i], NULL);
    }

    for (int i = 0; i < NUM_PHILOSOPHERS; i++) {
        pthread_mutex_destroy(&chopsticks[i]);
    }

    return 0;
}