//////// Codice didattico Prof. Marco Tarini - Università di Milano
//////// Rivisto, commentato e adattato per viewport Shadertoy da 
//////// Enrico Puppo - Università di Genova
// per testare questo codice, puoi inserirlo (cut and paste)
// su https://www.shadertoy.com/new


//////// IL NOSTRO PRIMO RAY TRACER

// parametri dela camera (costanti)
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

// SCENA
Sfera sferaUno = Sfera( vec3(0.0,0.0,5.0) , 0.5 );


// un dato raggio interseca una data sfera?
bool intersect( Raggio r, Sfera s ) {
    // punti su s: punti p t.c. ||p - s.centro||^2 - s.raggio^2 = 0
    // punti su r: punti p esprimibili come  p = r.pos + k * r.dir  
    // si costruisce un'equazione di secondo grado con incognita k:
    // k*k*a + k*b + c = 0
    // calcoliamo a, b, c sostituendo l'equazione del raggio in quella della sfera
    vec3 d = r.pos - s.centro; 
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


// restituisce il colore pixelColor per il pixel di coordnate pixelPos
void mainImage( out vec4 pixelColor, 
                 in vec2 pixelPos )
{
    // passiamo da coordinate intere pixel a coordinate di clip
    // (iResolution è la risoluzione dell'immagine di output) 
    // offset calcolato per centrare la vista
    float res = min(iResolution.x,iResolution.y);
    vec2 offset = vec2(0.5*iResolution.x/res,0.5*iResolution.y/res);
    vec2 clipPos = pixelPos / res - offset;
    pixelColor = vec4( ray_cast(clipPos),  0.0  );
}
