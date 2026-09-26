#include <stdio.h> 
#include <stdlib.h> 
#include <math.h> 
#include <limits.h>
#include <time.h>
#include <mpi.h> 

#define MAX_NUMEROS 10000

#define MPI_SOLUCION_ENCONTRADA 0
#define MPI_BUSCAR_PRIMO 1
#define MPI_ESCLAVO_PREPARADO 2
#define MPI_FIN 3

typedef unsigned long long Entero_grande;
#define ENTERO_MAS_GRANDE  ULLONG_MAX

int es_primo( Entero_grande n ) {
  int p;
  Entero_grande i, s;

  p = (n % 2 != 0 || n == 2);

  if (p) {
    s = sqrt(n);

    for (i = 3; p && i <= s; i += 2)
      if (n % i == 0) p = 0;
  }

  return p;
}

Entero_grande generar_numero( ) {
  Entero_grande aux = rand();
  aux = ( aux << 32 ) + rand();
  if( !( aux % 2 ) ) aux++;
  return aux;
}

int main(int argc,char *argv[]) {
  int rank, size, primos_solicitados;
  MPI_Status status;
  
  MPI_Init(&argc,&argv); 
  MPI_Comm_size(MPI_COMM_WORLD,&size); 
  MPI_Comm_rank(MPI_COMM_WORLD,&rank);
  
  if (size<2) {
     printf("El número minimo de procesos es de 2\n");
     MPI_Finalize(); 
     return 0;
  }
  
  if (argc>=2) sscanf(argv[1],"%d",&primos_solicitados);
  else primos_solicitados = 1;

  if (rank == 0) {
      /* Código del maestro */
      double t1, t2;
      t1 = MPI_Wtime();
      
      int k = 0;                     // primos encontrados
      int esclavos = size - 1;       // número de esclavos activos
      srand(time(NULL));             // semilla para números aleatorios
      
      while (esclavos > 0) {
          Entero_grande num;
          MPI_Status status;
          
          // Recibir mensaje de cualquier esclavo
          MPI_Recv(&num, 1, MPI_UNSIGNED_LONG_LONG, MPI_ANY_SOURCE, MPI_ANY_TAG,
                   MPI_COMM_WORLD, &status);
          
          int source = status.MPI_SOURCE;
          int tag = status.MPI_TAG;
          
          // Si el mensaje contiene un primo y aún no hemos terminado
          if (tag == MPI_SOLUCION_ENCONTRADA && k < primos_solicitados) {
              printf("Primo encontrado: %llu\n", num);
              k++;
          }
          
          // Decidir si enviamos más trabajo o terminamos con este esclavo
          if (k < primos_solicitados) {
              Entero_grande nuevo_num = generar_numero();
              MPI_Send(&nuevo_num, 1, MPI_UNSIGNED_LONG_LONG, source,
                       MPI_BUSCAR_PRIMO, MPI_COMM_WORLD);
          } else {
              // Enviar mensaje de terminación
              Entero_grande dummy = 0;
              MPI_Send(&dummy, 1, MPI_UNSIGNED_LONG_LONG, source,
                       MPI_FIN, MPI_COMM_WORLD);
              esclavos--;
          }
      }
      
      t2 = MPI_Wtime();
      printf("Tiempo = %f s.\n", t2 - t1);
      
  } else { 
      /* Código del esclavo */
      Entero_grande dummy = 0;
      
      // Enviar mensaje inicial al maestro
      MPI_Send(&dummy, 1, MPI_UNSIGNED_LONG_LONG, 0,
               MPI_ESCLAVO_PREPARADO, MPI_COMM_WORLD);
      
      int continuar = 1;
      while (continuar) {
          Entero_grande num;
          MPI_Status status;
          
          // Recibir mensaje del maestro
          MPI_Recv(&num, 1, MPI_UNSIGNED_LONG_LONG, 0, MPI_ANY_TAG,
                   MPI_COMM_WORLD, &status);
          
          if (status.MPI_TAG == MPI_FIN) {
              continuar = 0;
          } else { // MPI_BUSCAR_PRIMO
              if (es_primo(num)) {
                  MPI_Send(&num, 1, MPI_UNSIGNED_LONG_LONG, 0,
                           MPI_SOLUCION_ENCONTRADA, MPI_COMM_WORLD);
              } else {
                  MPI_Send(&dummy, 1, MPI_UNSIGNED_LONG_LONG, 0,
                           MPI_ESCLAVO_PREPARADO, MPI_COMM_WORLD);
              }
          }
      }
  }
  
  MPI_Finalize(); 
  return 0;
}