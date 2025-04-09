#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include "my_semaphore.h"

#define N 20  // Total number of passengers
#define C 5   // Bus capacity

// Shared variables and synchronization primitives
my_semaphore bus_capacity;      // Controls available seats on the bus
my_semaphore passengers_on_bus; // Counts passengers on the bus
my_semaphore tour_done;         // Signals that the tour is done
my_semaphore all_exited;        // Signals that all passengers have exited

int passengers_count = 0;       // Number of passengers currently on the bus
pthread_mutex_t count_mutex;    // Protects access to passengers_count

// Function representing the bus behavior
void* bus_thread(void* arg) {
    while (1) {
        printf("Bus: Waiting for passengers to board...\n");
        
        // Wait until the bus is full (C passengers)
        for (int i = 0; i < C; i++) {
            my_sem_wait(&passengers_on_bus);
        }
        
        printf("Bus: Full! Starting the tour...\n");
        
        // Simulate the tour
        sleep(2);
        
        printf("Bus: Tour completed. Letting passengers off...\n");
        
        // Signal that the tour is done
        for (int i = 0; i < C; i++) {
            my_sem_signal(&tour_done);
        }
        
        // Wait until all passengers have exited
        my_sem_wait(&all_exited);
        
        printf("Bus: All passengers have exited. Ready for new passengers.\n");
        
        // Reset bus capacity for new passengers
        for (int i = 0; i < C; i++) {
            my_sem_signal(&bus_capacity);
        }
    }
    
    return NULL;
}

// Function representing a passenger behavior
void* passenger_thread(void* arg) {
    int id = *(int*)arg;
    free(arg);
    
    while (1) {
        printf("Passenger %d: Waiting to board the bus.\n", id);
        
        // Try to get a seat on the bus
        my_sem_wait(&bus_capacity);
        
        // Board the bus
        pthread_mutex_lock(&count_mutex);
        passengers_count++;
        printf("Passenger %d: Boarded the bus. [%d/%d]\n", id, passengers_count, C);
        
        // If this passenger makes the bus full, signal to start the tour
        if (passengers_count == C) {
            printf("Passenger %d: I'm the last to board. Bus is now full.\n", id);
        }
        pthread_mutex_unlock(&count_mutex);
        
        // Signal that a passenger is on the bus
        my_sem_signal(&passengers_on_bus);
        
        // Wait for the tour to complete
        my_sem_wait(&tour_done);
        
        // Exit the bus
        pthread_mutex_lock(&count_mutex);
        passengers_count--;
        printf("Passenger %d: Exiting the bus. [%d remaining]\n", id, passengers_count);
        
        // If this passenger is the last to exit, signal the bus
        if (passengers_count == 0) {
            printf("Passenger %d: I'm the last to exit. Bus is now empty.\n", id);
            my_sem_signal(&all_exited);
        }
        pthread_mutex_unlock(&count_mutex);
        
        // Simulate passenger doing other activities before next tour
        sleep(rand() % 5 + 1);
    }
    
    return NULL;
}

int main() {
    pthread_t bus;
    pthread_t passengers[N];
    
    // Initialize synchronization primitives
    pthread_mutex_init(&count_mutex, NULL);
    my_sem_init(&bus_capacity, C);      // Initially, there are C seats available
    my_sem_init(&passengers_on_bus, 0); // Initially, no passengers on the bus
    my_sem_init(&tour_done, 0);         // Initially, tour has not started
    my_sem_init(&all_exited, 0);        // Initially, no one has exited
    
    // Create bus thread
    pthread_create(&bus, NULL, bus_thread, NULL);
    
    // Create passenger threads
    for (int i = 0; i < N; i++) {
        int* id = malloc(sizeof(int));
        *id = i + 1;
        pthread_create(&passengers[i], NULL, passenger_thread, id);
    }
    
    // Join threads (this will never happen in this example as the loops are infinite)
    pthread_join(bus, NULL);
    for (int i = 0; i < N; i++) {
        pthread_join(passengers[i], NULL);
    }
    
    // Clean up
    pthread_mutex_destroy(&count_mutex);
    my_sem_destroy(&bus_capacity);
    my_sem_destroy(&passengers_on_bus);
    my_sem_destroy(&tour_done);
    my_sem_destroy(&all_exited);
    
    return 0;
}
