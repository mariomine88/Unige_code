#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <omp.h>   // Aggiunto per OpenMP

int main( int argc, char *argv[] ) {
  if( argc<3 ) {
    fprintf(stderr,"Uso: %s priedras capacidad\n",argv[0]);
    return -1;
  }
  double valor;
  int capacidad;
  int n, c;
  int cap, k, y, x, resto;
  long max;
  double val;
  sscanf(argv[1],"%d",&n);
  sscanf(argv[2],"%d",&c);
  printf("Problema de la mochila con %d piedras y capacidad = %d\n",n,c);
  int w[n];
  double p[n];
  int solucion[n];
  int s[n];

  /* Generando pesos y valores aleatoriamente */
  for( int i=0; i<n; i++ ) {
    w[i] = rand() % 10;
    p[i] = (double) rand() / RAND_MAX;
  }
#ifdef CHECK
  printf("Pesos = [");
  for( int i=0; i<n; i++ ) {
    printf("%5d",w[i]);
  }
  printf("   ]\n");
  printf("Valores = [");
  for( int i=0; i<n; i++ ) {
    printf("%6.2f",p[i]);
  }
  printf("   ]\n");
#endif

  valor = 0;
  capacidad = c;
  memset(solucion,0,n*sizeof(int));
  max = (long) powl(2,n);
  if( max < 0 ) {
    printf("El problema no se puede calcular\n");
    return 0;
  }

  // Aggiunta della direttiva OpenMP per parallelizzare il ciclo principale
  #pragma omp parallel for private(x, cap, val, k, y, resto, s) shared(w, p, c, n, max, valor, capacidad, solucion)
  for( x=0; x<max; x++ ) {
    cap = c;
    val = 0;
    k = 0;
    memset(s,0,n*sizeof(int));
    y = x;
    while( y>0 && cap>=0 ) {
      resto = y%2;
      if( resto ) {
        cap -= w[k];
        val += p[k];
      }
      s[k] = resto;
      y /= 2;
      k++;
    }
    if( cap>=0 ) {
      // Sezione critica per aggiornare le variabili condivise in modo sicuro
      #pragma omp critical
      {
        if( val >= valor ) {
          valor = val;
          capacidad = cap;
          memcpy( solucion, s, n*sizeof(int) );
        }
      }
    }
  }

#ifdef CHECK
  printf("Solucion = [");
  for( int i=0; i<n; i++ ) {
    printf("%2d",solucion[i]);
  }
  printf(" ]\n");
#endif
  printf("Valor = %f\n",valor);
  printf("Capacidad restante = %d\n",capacidad);

  return 0;
}