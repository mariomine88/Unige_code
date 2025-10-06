//////// Codice didattico Prof. Marco Tarini - Università di Milano
//////// Rivisto e commentato da Enrico Puppo - Università di Genova
// per testare questo codice, puoi usare l'estensione glslCanvas di VSC

// RAYTRACER per sfere con calcolo dello shading completo
// 
// - aggiungiamo tutti i coefficienti di materiale
// - intersect restituisce anche il valore k del punti di intersezione
// - aggiungiamo la componente speculare
//

precision highp float;
uniform vec2 u_resolution;

// parametri della camera (costanti)
    const float LUNGHEZZA_FOCALE = 2.0;
    const vec3 POV = vec3( 0.0 , 0.0 , 0.0 ); // Point of View

// parametri generali dello shader
    const vec3 COLORE_OGGETTO = vec3( 1.0, 0.0, 0.0);
    const vec3 COLORE_SFONDO = vec3( 0.2, 0.5, 1.0);
    const vec3 ROSSO = vec3( 1.0, 0.2, 0.2);
    const vec3 GIALLO = vec3( 0.7, 0.7, 0.0);
    const vec3 VERDE = vec3( 0.0, 0.8, 0.2);

// struttura per i materiali
struct Materiale {
    vec3 amb;
    vec3 diff;
    vec3 spec;
    float lucentezza;
};

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
    Materiale mat;
};

// scena
const Materiale m1 = Materiale(vec3(0.2),ROSSO*0.7,vec3(0.4),50.0);
Sfera sferaUno = Sfera( vec3(0.0,0.0,5.0) , 0.5, m1 );
// luci
vec3 pos_luce     = vec3(5.0,5,0.0);
vec3 colore_luce     = vec3(1.0);
vec3 luce_ambiente = vec3(0.3, 0.28, 0.15);


// il raggio r interseca la sfera s? se sì:
// restituisce il parametro di intersezione k e la normale n
bool intersect( in Raggio r, in Sfera s, out float k, out vec3 nor ) {
  vec3 d = s.centro-r.pos; 
  float a = 1.0;
  float b = -2.0*dot(d , r.dir );
  float c = dot(d,d) - s.raggio * s.raggio; 
  float delta = b*b - 4.0*a*c; 
  if (delta<0.0) return false; // no intersezione!

  k = (-b -sqrt(delta) ) / 2.0*a;
  if (k<0.0) return false; // intersezione c'e' ma DIETRO la partenza del raggio
  
  nor = (r.pos + k*r.dir - s.centro)/s.raggio;
  return true;
}

// restituisce il Raggio per il pixel in coordinate clip (p.x,p.y)
Raggio raggio_primario( vec2 p ){
  vec3 pixel_pos; // posizione del pixel sul piano immagine
  pixel_pos.xy = p;
  pixel_pos.z = LUNGHEZZA_FOCALE;
  Raggio r;
  r.pos = POV;
  r.dir = normalize( pixel_pos - POV );
  return r; 
}

// dato un pixel di coordiante clip_pos, trova il suo colore
vec3 ray_cast( vec2 clip_pos ){
  Raggio r = raggio_primario( clip_pos );
  vec3 col; 
  vec3 n; float k;
  if (intersect( r, sferaUno, k, n)) { 
    vec3 punto_colpito = r.pos + k*r.dir;
    vec3 verso_luce = normalize(pos_luce - punto_colpito);
    vec3 verso_occhio = normalize(POV-punto_colpito);
    // equazione dell'illuminazione
	  Materiale mat = sferaUno.mat; 
    float lambert = dot( n, verso_luce ); // legge del coseno
    float specular = pow(dot(n,normalize(verso_occhio+verso_luce)),mat.lucentezza);
 	  col = mat.amb*luce_ambiente +
          mat.diff*colore_luce*lambert +
          mat.spec*specular;
    col = clamp(col,0.0,1.0);
  } else col = COLORE_SFONDO; 
  
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
