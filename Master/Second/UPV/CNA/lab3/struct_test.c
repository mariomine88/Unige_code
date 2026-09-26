#include <stdio.h>
#include <string.h>
#include <stddef.h>
#include <mpi.h>

int main( int argc, char *argv[] ) {

  struct tipo_punto {
    int i;
    double x, y;
    double masa;
    char nombre[10];
  };

  struct tipo_punto punto_a_enviar, punto_a_recibir;

  int rank, size;
  MPI_Init(&argc,&argv);
  MPI_Comm_rank( MPI_COMM_WORLD, &rank );
  MPI_Comm_size( MPI_COMM_WORLD, &size );

  /****************************************
   Construcción del tipo de dato MPI
   ****************************************/
  MPI_Datatype mpi_tipo_punto;
  int block_lengths[5] = {1, 1, 1, 1, 10};
  MPI_Datatype types[5] = {MPI_INT, MPI_DOUBLE, MPI_DOUBLE, MPI_DOUBLE, MPI_CHAR};
  MPI_Aint displacements[5];
  displacements[0] = offsetof(struct tipo_punto, i);
  displacements[1] = offsetof(struct tipo_punto, x);
  displacements[2] = offsetof(struct tipo_punto, y);
  displacements[3] = offsetof(struct tipo_punto, masa);
  displacements[4] = offsetof(struct tipo_punto, nombre);

  MPI_Type_create_struct(5, block_lengths, displacements, types, &mpi_tipo_punto);
  MPI_Type_commit(&mpi_tipo_punto);

  if( rank==0 ) {
    punto_a_enviar.i = 100;
    punto_a_enviar.x = 1.3;
    punto_a_enviar.y = 1.8;
    punto_a_enviar.masa = 2.1E-6;
    strcpy(punto_a_enviar.nombre,"muon01");
  }

  /****************************************
   Envio del dato al anillo y recepción
   ****************************************/
  if (size == 1) {
    if (rank == 0) punto_a_recibir = punto_a_enviar;
  } else {
    if (rank == 0) {
      MPI_Send(&punto_a_enviar, 1, mpi_tipo_punto, 1, 0, MPI_COMM_WORLD);
      MPI_Recv(&punto_a_recibir, 1, mpi_tipo_punto, size-1, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    } else {
      MPI_Recv(&punto_a_recibir, 1, mpi_tipo_punto, rank-1, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
      MPI_Send(&punto_a_recibir, 1, mpi_tipo_punto, (rank+1)%size, 0, MPI_COMM_WORLD);
    }
  }

  /* Los valores deben ser los mismos */
  if( rank==0 ) {
    printf("i = %d\n",punto_a_recibir.i);
    printf("x = %f\n",punto_a_recibir.x);
    printf("y = %f\n",punto_a_recibir.y);
    printf("masa = %e\n",punto_a_recibir.masa);
    printf("nombre = %s\n",punto_a_recibir.nombre);
  }

  /****************************************
   Destrucción del tipo de dato MPI
   ****************************************/
  MPI_Type_free(&mpi_tipo_punto);
  MPI_Finalize();
  return 0;
}