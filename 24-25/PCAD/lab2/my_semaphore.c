#include "my_semaphore.h"

int my_sem_init(my_semaphore *ms, unsigned int v) {
    ms->V = v;
    
    if (pthread_mutex_init(&ms->lock, NULL) != 0) {
        return -1;
    }
    
    if (pthread_cond_init(&ms->varcond, NULL) != 0) {
        pthread_mutex_destroy(&ms->lock);
        return -1;
    }
    
    return 0;
}

int my_sem_wait(my_semaphore *ms) {
    pthread_mutex_lock(&ms->lock);
    
    while (ms->V == 0) {
        pthread_cond_wait(&ms->varcond, &ms->lock);
    }
    
    ms->V--;
    
    pthread_mutex_unlock(&ms->lock);
    return 0;
}

int my_sem_signal(my_semaphore *ms) {
    pthread_mutex_lock(&ms->lock);
    
    ms->V++;
    pthread_cond_signal(&ms->varcond);
    
    pthread_mutex_unlock(&ms->lock);
    return 0;
}

int my_sem_destroy(my_semaphore *ms) {
    pthread_mutex_destroy(&ms->lock);
    pthread_cond_destroy(&ms->varcond);
    return 0;
}
