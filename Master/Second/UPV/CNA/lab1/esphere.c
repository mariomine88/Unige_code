#include <stdio.h> 
#include <stdlib.h>
#include <math.h> 
#include <mpi.h>      // Aggiunto per MPI
#include <time.h>     // Per time()

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

  // 3. Divisione dei punti tra i processi
  unsigned long int local_puntos = max_puntos / size;
  if (rank == 0) {
    local_puntos += max_puntos % size;  // il processo 0 prende il resto
  }

  // 4. Seed diverso per ogni processo
  srand(time(NULL) + rank);

  // 5. Ciclo locale
  double local_aciertos = 0.0;
  for (unsigned long int i = 0; i < local_puntos; i++) {
     double x = (((double) rand()) / RAND_MAX) * radio;
     double y = (((double) rand()) / RAND_MAX) * radio;
     double z = (((double) rand()) / RAND_MAX) * radio;
     if ((x*x + y*y + z*z) <= (radio*radio)) {
         local_aciertos += 1.0;
     }
  }

  // 6. Comunicazione punto-punto
  double total_aciertos = 0.0;

  if (rank == 0) {
    // Il processo 0 parte con il suo contributo
    total_aciertos = local_aciertos;

    // Riceve dagli altri processi
    for (int i = 1; i < size; i++) {
      double recv_aciertos;
      MPI_Recv(&recv_aciertos, 1, MPI_DOUBLE, i, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
      total_aciertos += recv_aciertos;
    }

    // 7. Calcolo finale e stampa
    double volumen = radio * radio * radio * total_aciertos / max_puntos * 8;
    printf("Volumen calculado = %f, volumen esfera = %f. \n",
           volumen, 4.0 * M_PI * radio * radio * radio / 3.0);

  } else {
    // Gli altri processi inviano il loro contributo al processo 0
    MPI_Send(&local_aciertos, 1, MPI_DOUBLE, 0, 0, MPI_COMM_WORLD);
  }

  // 8. Finalizza MPI
  MPI_Finalize();
  return 0;
}