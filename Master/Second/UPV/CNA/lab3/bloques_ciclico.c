#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <mpi.h>

/* Almacenamiento por columnas: A(i,j) = A[(j)*m + i] */
#define A(i,j) A[(j)*m+(i)]
#define Asaved(i,j) Asaved[(j)*m+(i)]

double norm2( int n, double *v );

int main( int argc, char *argv[] ) {

  MPI_Init(&argc,&argv);
  int size, rank; 
  MPI_Comm_size (MPI_COMM_WORLD, &size); 
  MPI_Comm_rank (MPI_COMM_WORLD, &rank);
  if( argc<3 ) {
    if( rank==0 ) printf("Usage: mpirun -np %d %s n block_size\n",size,argv[0]);
    MPI_Finalize();
    return 0;
  }
  int m, n;
  sscanf(argv[1],"%d",&m);
  int blk;
  sscanf(argv[2],"%d",&blk);
  if( blk*size > m ) {
    if( rank==0 ) printf("blk debería ser más pequeño\n");
    MPI_Finalize();
    return 0;
  }

  double *A, *Asaved;
  int blocks_per_process = (m + blk*size - 1) / (blk*size);
  n = blk * size * blocks_per_process;  // número total de columnas (incluye padding)

  if( rank==0 ) {
    A = (double *) malloc( m*n*sizeof(double) );
    Asaved = (double *) malloc( m*n*sizeof(double) );
    // Inicializar a cero (incluyendo padding)
    for( int i=0; i<m*n; i++ ) {
      A[i] = 0.0;
      Asaved[i] = 0.0;
    }
    // Llenar la parte m x m simétrica
    for( int i=0; i<m; i++ ) {
      A(i,i) = Asaved(i,i) = ( (double) rand() ) / RAND_MAX;
      for( int j=i+1; j<m; j++ ) {
        A(i,j) = A(j,i) = Asaved(i,j) = Asaved(j,i) = ( (double) rand() ) / RAND_MAX;
      }
    }
  }

  int cols_per_proc = blocks_per_process * blk;
  double *B = (double *) malloc( m * cols_per_proc * sizeof(double) );

  /* Creación del tipo de dato MPI:
     blocks_per_process bloques de blk columnas cada uno.
     Cada columna tiene m elementos.
     El stride entre bloques es blk*size columnas = blk*size*m elementos.
  */
  MPI_Datatype col_type;
  MPI_Type_vector(blocks_per_process, blk*m, blk*size*m, MPI_DOUBLE, &col_type);
  MPI_Type_commit(&col_type);

  /* Distribución de la matriz A entre los procesos */
  if( rank == 0 ) {
    // Proceso 0: copiar sus propios bloques a B
    for( int b=0; b<blocks_per_process; b++ ) {
      int col_start = b * blk * size;  // columna inicial del bloque b para el proceso 0
      for( int i=0; i<m; i++ ) {
        for( int j=0; j<blk; j++ ) {
          B[b*blk*m + j*m + i] = A[(col_start + j)*m + i];
        }
      }
    }
    // Enviar a los demás procesos
    for( int p=1; p<size; p++ ) {
      MPI_Send( &A[p*blk*m], 1, col_type, p, 0, MPI_COMM_WORLD );
    }
  } else {
    MPI_Recv( B, m*cols_per_proc, MPI_DOUBLE, 0, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE );
  }

  /* Recogida de la matriz desde los procesos en la matriz Asaved del root */
  if( rank == 0 ) {
    // Recibir de los demás procesos directamente en Asaved usando el tipo derivado
    for( int p=1; p<size; p++ ) {
      MPI_Recv( &Asaved[p*blk*m], 1, col_type, p, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE );
    }
    // Copiar de B a Asaved para el proceso 0
    for( int b=0; b<blocks_per_process; b++ ) {
      int col_start = b * blk * size;
      for( int i=0; i<m; i++ ) {
        for( int j=0; j<blk; j++ ) {
          Asaved[(col_start + j)*m + i] = B[b*blk*m + j*m + i];
        }
      }
    }
  } else {
    MPI_Send( B, m*cols_per_proc, MPI_DOUBLE, 0, 0, MPI_COMM_WORLD );
  }

  /* Comprobación del resultado */
  if( rank == 0 ) {
    for( int i=0; i<m; i++ ) {
      for( int j=0; j<n; j++ ) {
        Asaved(i,j) -= A(i,j);
      }
    }
    printf("Error = %f\n", norm2(m*n, Asaved));
  }

  MPI_Type_free( &col_type );
  free(B);
  if( rank==0 ) {
    free(Asaved);
    free(A);
  }
  MPI_Finalize();
  return 0;
}

double norm2( int n, double *v ) {
  double x = 0.0;
  for( int i=0; i<n; i++ ) {
    x += v[i]*v[i];
  }
  return sqrt(x);
}