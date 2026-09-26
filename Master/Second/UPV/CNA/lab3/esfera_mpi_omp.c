#include <stdio.h> 
#include <stdlib.h>
#include <math.h> 
#include <mpi.h>      // Per MPI
#include <time.h>     // Per time()
#include <omp.h>      // Per OpenMP

int main(int argc, char *argv[]) {

  int rank, size;

  // 1. Inizializza MPI
  MPI_Init(&argc, &argv);
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  MPI_Comm_size(MPI_COMM_WORLD, &size);

  // 2. Controllo argomenti
  if (argc < 2) {
    if (rank == 0) {
      printf("Uso: %s radio [max_puntos]\n", argv[0]);
    }
    MPI_Finalize();
    return 0;
  }

  double radio;
  sscanf(argv[1], "%lf", &radio);

  double max_puntos_d = 10E7;
  if (argc > 2) {
    sscanf(argv[2], "%lf", &max_puntos_d);
  }

  // Convertiamo in intero senza segno
  unsigned long int max_puntos = (unsigned long int) max_puntos_d;

  if (rank == 0) {
    printf("Calculo del volumen de una esfera de radio %.2f (max_puntos = %.0e)\n",
           radio, max_puntos_d);
  }

  // 3. Divisione dei punti tra i processi MPI
  unsigned long int local_puntos = max_puntos / size;
  if (rank == 0) {
    local_puntos += max_puntos % size;  // il processo 0 prende il resto
  }

  // 4. Ciclo locale con OpenMP (riduzione su local_aciertos)
  double local_aciertos = 0.0;

  #pragma omp parallel reduction(+:local_aciertos)
  {
      // Seed diverso per ogni thread e processo
      unsigned int seed = time(NULL) + rank * 1000 + omp_get_thread_num();
      #pragma omp for
      for (unsigned long int i = 0; i < local_puntos; i++) {
         double x = (((double) rand_r(&seed)) / RAND_MAX) * radio;
         double y = (((double) rand_r(&seed)) / RAND_MAX) * radio;
         double z = (((double) rand_r(&seed)) / RAND_MAX) * radio;
         if ((x*x + y*y + z*z) <= (radio*radio)) {
             local_aciertos += 1.0;
         }
      }
  }

  // 5. Comunicazione collettiva: somma di tutti i local_aciertos nel processo 0
  double total_aciertos = 0.0;
  MPI_Reduce(&local_aciertos, &total_aciertos, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

  // 6. Solo il processo 0 calcola e stampa il risultato
  if (rank == 0) {
    double volumen = radio * radio * radio * total_aciertos / max_puntos * 8;
    printf("Volumen calculado = %f, volumen esfera = %f. \n",
           volumen, 4.0 * M_PI * radio * radio * radio / 3.0);
  }

  // 7. Finalizza MPI
  MPI_Finalize();
  return 0;
}