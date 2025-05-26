//////// Codice didattico Prof. Marco Tarini - Università di Milano
//////// Rivisto e commentato da Enrico Puppo - Università di Genova
// per testare questo codice, puoi usare l'estensione glslCanvas di VSC

// RAYTRACER per sfere con calcolo delle normali
// 
// - La funzione intersect restituisce la normale del punto colpito
// - La normale viene mostrata a schermo come colore RGB
//

precision highp float;
uniform vec2 u_resolution;

// parametri della camera (costanti)
    const float LUNGHEZZA_FOCALE = 2.0;
    const vec3 POV = vec3( 0.0 , 0.0 , 0.0 ); // Point of View

// parametri generali dello shader
    const vec3 COLORE_OGGETTO = vec3( 1.0, 0.0, 0.0);
    const vec3 COLORE_SFONDO = vec3( 0.2, 0.5, 1.0);


// struttura Raggio (semiretta) 
// che parte da pos e va in direzione dir
struct Raggio {
    vec3 pos; // punto di origine del raggio
    vec3 dir; // versore (vettore a norma 1)
};

// struttura Sfera (come modello implicito)
struct Sfera {
    vec3 centro;
    float raggio;
};

// scena
Sfera sferaUno = Sfera( vec3(0.0,0.0,5.0) , 0.5 );

// il raggio r interseca la sfera s?
bool intersect( in Raggio r, in Sfera s, out vec3 nor ) {
  vec3 d = s.centro-r.pos; 
  float a = 1.0;
  float b = -2.0*dot(d , r.dir );
  float c = dot(d,d) - s.raggio * s.raggio; 
  float delta = b*b - 4.0*a*c; 
  if (delta<0.0) return false;

  // calcolo il valore minimo di k
  float k = (-b -sqrt(delta) ) / 2.0*a;
  if (k<0.0) return false; // intersezione c'e' ma DIETRO la partenza del raggio  
  nor = (r.pos + k*r.dir - s.centro)/s.raggio;
  return true;
}

// restituisce il Raggio per il pixel in coordinate clip (p.x,p.y)
Raggio raggio_primario( vec2 p ){
  vec3 pixel_pos = vec3(p,LUNGHEZZA_FOCALE);
  Raggio r = Raggio(POV, normalize( pixel_pos - POV ));
  return r; 
}

// dato un pixel di coordiante clip_pos, trova il suo colore
vec3 ray_cast( vec2 clip_pos ){
  Raggio r = raggio_primario( clip_pos );
  float k; vec3 col; vec3 n;
  if (intersect(r , sferaUno , n)) 
    col = ( n + vec3(1.0) )/2.0; // mostriamo le normali come colore
  else col = COLORE_SFONDO;
  return col;
}

// restituisce il colore gl_FragColor per il pixel di coordnate gl_FragCoord
void main()
{
  float res = min(u_resolution.x,u_resolution.y);
  vec2 offset = vec2(0.5*u_resolution.x/res,0.5*u_resolution.y/res);
  vec2 adjust_view = vec2(0,0); //vec2(0,0.15);
  vec2 clipPos = gl_FragCoord.xy / res - offset + adjust_view;
  gl_FragColor = vec4( ray_cast(clipPos),  1.0  );
}
