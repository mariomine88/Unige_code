//////// Codice didattico Prof. Marco Tarini - Università di Milano
//////// Rivisto e commentato da Enrico Puppo - Università di Genova
// per testare questo codice, puoi usare l'estensione glslCanvas di VSC

// RAYTRACER per sfere multiple e occlusioni
// 
// - aggiungiamo una seconda sfera
// - modifichiamo intersect in modo che si accorga delle occlusioni
//

precision highp float;
uniform vec2 u_resolution;

// parametri della camera (costanti)
    const float LUNGHEZZA_FOCALE = 2.0;
    const vec3 POV = vec3( 0.0 , 0.0 , 0.0 ); // Point of View

// parametri generali dello shader
    const vec3 COLORE_SFONDO = vec3( 0.2, 0.5, 1.0);
    const vec3 ROSSO = vec3( 1.0, 0.2, 0.2);
    const vec3 GIALLO = vec3( 0.7, 0.7, 0.0);
    const vec3 VERDE = vec3( 0.0, 0.8, 0.2);
    float MAX_DIST = 100.0; // da questa distanza in poi solo sfondo
    float EPSILON = 0.001;

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

// struttura per un piano (PRIMITIVA di rendering)
struct Piano {
  vec3 punto;
  vec3 normale; 
  Materiale mat;
};

// scena
const Materiale BACKGROUND = Materiale(COLORE_SFONDO,vec3(0.0),vec3(0.0),0.0);
const Materiale m1 = Materiale(ROSSO*0.3,ROSSO*0.7,vec3(0.4),50.0);
const Materiale m2 = Materiale(VERDE*0.3,VERDE*0.7,vec3(0.4),50.0);
const Materiale m3 = Materiale(GIALLO*0.3,GIALLO*0.7,vec3(0.4),50.0);
Sfera sferaUno = Sfera( vec3(0.0,0.0,5.0) , 0.5, m1 );
Sfera sferaDue = Sfera( vec3(-0.1,0.4,4.8) , 0.3, m2 );
Piano pianoUno = Piano( vec3(0.0,-0.35,0.0) , vec3(0.0,1.0,0.0), m3 );
// luci
vec3 pos_luce     = vec3(5.0,5.0,-3.0);
vec3 colore_luce     = vec3(1.0);
vec3 luce_ambiente = vec3(0.5);


// il raggio r interseca il piano p? (entro kMax di distanza)
// Se sì sovrascrive: mat materiale del punto colpito,
// parametro di intersezione kMax e sua normale nor
bool intersect( in Raggio r , in Piano p , 
                inout float kMax, inout Materiale mat, inout vec3 nor ) {
  // punti su r: punti q esprimibili come  q = r.pos + k * r.dir  
  // punti su p: punti q t.c.  dot(q - p.punto , p.normale) == 0
  // cerchiamo un punto (se esiste) sia su r che su p, cioè
  // cerchiamo un k>0 t.c. 
  // dot(r.pos + k * r.dir - p.punto , p.normale) == 0
  
  float dn = dot( p.normale , r.dir );
  if (dn == 0.0 ) return false; // piano parallelo a raggio
  float k = dot (p.punto - r.pos, p.normale) / dn;
  if (k>kMax) return false; // occlusione!
  if (k<0.0) return false; // intersezione c'e' ma DIETRO la partenza del raggio
  kMax = k;
  mat = p.mat;
  nor = p.normale;
  return true;
}

// il raggio r interseca la sfera s? se sì sovrascrive:
// parametro di intersezione kMax, la normale n e il materiale mat
bool intersect( in Raggio r, in Sfera s, 
                inout float kMax, inout Materiale mat, inout vec3 nor ) {
  vec3 d = s.centro-r.pos; 
  float a = 1.0;
  float b = -2.0*dot(d , r.dir );
  float c = dot(d,d) - s.raggio * s.raggio; 
  float delta = b*b - 4.0*a*c; 
  if (delta<0.0) return false; // no intersezione!

  float k = (-b -sqrt(delta) ) / 2.0*a;
  if (k>kMax) return false; // occlusione!
  if (k<0.0) return false; // intersezione c'e' ma DIETRO la partenza del raggio
  
  kMax = k;
  mat = s.mat;
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

// calcola il punto di intersezione più vicino
// tra tutti gli oggetti nella scena
void intersect_scene( in Raggio r, out float k, out Materiale mat, out vec3 nor ) {
  k = MAX_DIST;
  mat = BACKGROUND;
  nor = vec3(0,0,0.0);
  intersect( r, sferaUno , k , mat , nor ); 
  intersect( r, sferaDue , k , mat , nor );
  intersect( r, pianoUno , k , mat , nor );
  // ora se k < 100 allora ho colpito qualcosa: 
  // mat è il suo materiale e nor è la sua normale
}

// dato un pixel di coordiante clip_pos, trova il suo colore
vec3 ray_cast( vec2 clip_pos ){
  Raggio r = raggio_primario( clip_pos );
  vec3 col; 
  vec3 n; float k;
	Materiale mat; 
  intersect_scene( r, k, mat, n); 
  if (k<MAX_DIST) {
  vec3 punto_colpito = r.pos + (k-EPSILON)*r.dir;
  vec3 verso_luce = normalize(pos_luce - punto_colpito);
  vec3 verso_occhio = normalize(POV-punto_colpito);
  // equazione dell'illuminazione
  float lambert = dot( n, verso_luce ); // legge del coseno
  float specular = pow(dot(n,normalize(verso_occhio+verso_luce)),mat.lucentezza);
 	col = mat.amb*luce_ambiente +
          mat.diff*colore_luce*lambert +
          mat.spec*specular;
  // calcolo ombra con raggio secondario
  r = Raggio( punto_colpito, verso_luce );
  k = MAX_DIST;
  Materiale dummy;
  intersect_scene(r, k, dummy, n);
  if (k<MAX_DIST) // il raggio secondario ha colpito un oggetto
    col *= 0.7;
    // col = mat.amb*luce_ambiente;
  } else col = COLORE_SFONDO;

  col = clamp(col,0.0,1.0);  
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
