//////// Codice didattico Prof. Marco Tarini - Università di Milano
//////// Rivisto e commentato da Enrico Puppo - Università di Genova
// per testare questo codice, puoi usare l'estensione glslCanvas di VSC

//////// IL NOSTRO PRIMO RAY TRACER
//
// - intersezione raggi con una sfera
// - colore uniforme
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


// un dato raggio interseca una data sfera?
bool intersect( Raggio r, Sfera s ) {
    // punti su s: punti p t.c. ||p - s.centro||^2 - s.raggio^2 = 0
    // punti su r: punti p esprimibili come  p = r.pos + k * r.dir  
    // si costruisce un'equazione di secondo grado con incognita k:
    // k*k*a + k*b + c = 0
    // calcoliamo a, b, c sostituendo l'equazione del raggio in quella della sfera
    vec3 d = s.centro-r.pos; 
    float a = 1.0;
    float b = -2.0*dot(d , r.dir );
    float c = dot(d,d) - s.raggio * s.raggio; 
    // c'è intersezione se e solo se il discriminante non è negativo
    float delta = b*b - 4.0*a*c;
    return (delta>0.0);    
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
    if (intersect( r, sferaUno ) ) return COLORE_OGGETTO; 
    else return COLORE_SFONDO;
}


// restituisce il colore gl_FragColor per il pixel di coordnate gl_FragCoord
void main()
{
    // passiamo da coordinate intere pixel a coordinate di clip
    // (u_resolution è la risoluzione dell'immagine di output) 
    float res = min(u_resolution.x,u_resolution.y);
    // offset calcolato in modo da averere il quadrato [0,1]x[0,1]
    // al centro dell'immagine
    vec2 offset = vec2(0.5*u_resolution.x/res,0.5*u_resolution.y/res);
    // adjust_view permette di traslare il quadrato
    vec2 adjust_view = vec2(0,0); //vec2(0,0.15);
    vec2 clipPos = gl_FragCoord.xy / res - offset + adjust_view;
    gl_FragColor = vec4( ray_cast(clipPos),  1.0  );
}
