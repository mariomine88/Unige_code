#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <mpi.h>

#define A(i,j) A[(i)+(j)*n]

int potencia( int n, double *A, double *lambda, double *q );

int main( int argc, char *argv[] ) {

  MPI_Init(&argc,&argv);
  int nprocs, rank; 
  MPI_Comm_size (MPI_COMM_WORLD, &nprocs); 
  MPI_Comm_rank (MPI_COMM_WORLD, &rank);
  if( argc<2 ) {
    if( rank==0 ) printf("Usage: mpirun -np %d %s n\n",nprocs,argv[0]);
    MPI_Finalize();
    return 0;
  }

  int n;
  sscanf(argv[1],"%d",&n);
  int cols_per_proc = n/nprocs + (n%nprocs>0?1:0);
  int total_cols = cols_per_proc*nprocs;

  double *A = NULL;                     // Initialize to NULL for non-root
  if( rank==0 ) {
    A = (double *) malloc( n*total_cols*sizeof(double) );
    // Zero the entire matrix to avoid garbage in padding columns
    memset(A, 0, n*total_cols*sizeof(double));
    for( int i=0; i<n; i++ ) {
      A(i,i) = ( (double) rand() ) / RAND_MAX;
      for( int j=i+1; j<n; j++ ) {
        A(i,j) = A(j,i) = ( (double) rand() ) / RAND_MAX;
      }
    }
#ifdef PRINT_MATRIZ
    for( int i=0; i<n; i++ ) {
      for( int j=0; j<n; j++ ) {
        printf("%16.10f",A(i,j));
      }
      printf("\n");
    }
#endif
  }

  // q must have length total_cols to accommodate padding columns
  double *q = (double *) malloc( total_cols*sizeof(double) );
  // Zero the padding elements (they will remain zero)
  for( int i=n; i<total_cols; i++ ) q[i] = 0.0;

  double lambda;
  int k = potencia( n, A, &lambda, q );

  if( rank==0 ) {
    printf("lambda = %f\n",lambda);
#ifdef PRINT_VECTOR
    for(int i=0; i<n; i++ ) {
      printf("q[%d] = %f\n",i,q[i]);
    }
#endif
    printf("iteraciones = %d\n",k);
  }

  free(q);                              // Free on all ranks
  if( rank==0 ) free(A);

  MPI_Finalize();
  return 0;
}

int matrizvector( int n, int cols_per_proc, double *A, double *q, double *z ) {
  int nprocs, rank;
  MPI_Comm_rank (MPI_COMM_WORLD, &rank);
  MPI_Comm_size (MPI_COMM_WORLD, &nprocs); 
  for( int i=0; i<n; i++ ) {
    z[i] = 0.0;
    for( int j=0; j<cols_per_proc; j++ ) {
      z[i] += A(i,j)*q[j]; 
    }
  }
  MPI_Allreduce(MPI_IN_PLACE, z, n, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
  return 0;
}

double norm2( int n, double *v ) {
  double x = 0.0;
  for( int i=0; i<n; i++ ) {
    x += v[i]*v[i];
  }
  return sqrt(x);
}

int scal( int n, double alfa, double *v, double *w ) {
  for( int i=0; i<n; i++ ) {
    w[i] = alfa*v[i];
  }
  return 0;
}

double dot( int n, double *v, double *w ) {
  double d = 0.0;
  for( int i=0; i<n; i++ ) {
    d += v[i]*w[i];
  }
  return d;
}

int potencia( int n, double *A, double *lambda, double *q ) {

  int nprocs, rank;
  MPI_Comm_size (MPI_COMM_WORLD, &nprocs); 
  MPI_Comm_rank (MPI_COMM_WORLD, &rank);
  int cols_per_proc = n/nprocs + (n%nprocs>0?1:0);
  int total_cols = cols_per_proc*nprocs;

  double *Aloc = (double *) malloc( n*cols_per_proc*sizeof(double) );
  
  MPI_Scatter(A, n*cols_per_proc, MPI_DOUBLE,
              Aloc, n*cols_per_proc, MPI_DOUBLE,
              0, MPI_COMM_WORLD);

  double *z = (double *) malloc( n*sizeof(double) );
  double alfa = 0.0;
  int k = 1;
  
  if( rank == 0 ) {
    for( int i=0; i<n; i++ ) {
      z[i] = A(i,0);  // first column
    }
  }
  MPI_Bcast(z, n, MPI_DOUBLE, 0, MPI_COMM_WORLD);

  if( rank == 0 ) {
    *lambda = A(0,0);
  }
  MPI_Bcast(lambda, 1, MPI_DOUBLE, 0, MPI_COMM_WORLD);

  while( fabs(*lambda-alfa)>2.220446049250313e-16 ) {
    k++;
    alfa = *lambda;
    scal( n, 1.0/norm2(n,z), z, q );
    // Now q has length total_cols, so &q[rank*cols_per_proc] is safe
    matrizvector( n, cols_per_proc, Aloc, &q[rank*cols_per_proc], z );
    *lambda = dot( n, q, z );
  }

  free(Aloc);
  free(z);
  return k;
}