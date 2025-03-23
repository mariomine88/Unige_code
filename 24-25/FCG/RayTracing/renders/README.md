## Set up

Per fare un render dobbiamo fare il setup, dobbiamo settare la telecamera e la scena.

### Configurazione della telecamera

Per la telecamera nelle shader dobbiamo impostare:
- `lookfrom`: la posizione della telecamera che metteremo a `vec3(0, 1, 6)`
- `lookat`: la coordinata che guarda sarà al centro del render che mettiamo a `vec3(0, 1, 0)`
- `cameraFov`: l'angolo di visuale che lasceremo principale a 70 gradi

### Configurazione della scena

Per il setting della scena dobbiamo andare nel codice C++ e settare le sfere in un array.
Ogni sfera ha 3 parametri:
1. Posizione (`vec3`)
2. Raggio (dimensione)
3. Materiale

Il materiale ha diversi parametri in questo ordine:
- `albedo`: colore diffuso (vec3)
- `specular`: colore speculare (vec3)
- `emission`: emissione di luce (vec3)
- `roughness`: rugosità della superficie
- `metallic`: metallicità
- `ior`: indice di rifrazione

Prima, mettiamo una sfera molto grande e grigia che sarà il nostro terreno:

```cpp
spheres.push_back({
    vec3(0.0f, -1000.0f, 0.0f), 1000.0f,
    Material(vec3(0.5f, 0.5f, 0.5f))
});
```

### Aggiunta di sfere colorate

Per creare una scena più interessante, possiamo aggiungere una serie di sfere colorate disposte in fila. Ecco un esempio di come creare cinque sfere con colori dell'arcobaleno:

```cpp
// Aggiungiamo una fila di sfere colorate
// Sfera rossa
spheres.push_back({
    vec3(-5.0f, 1.0f, 0.0f), 1.0f,
    Material(vec3(1.0f, 0.0f, 0.0f))
});

// Sfera gialla
spheres.push_back({
    vec3(-2.5f, 1.0f, 0.0f), 1.0f,
    Material(vec3(0.5f, 0.5f, 0.0f))
});

// Sfera verde
spheres.push_back({
    vec3(0.0f, 1.0f, 0.0f), 1.0f,
    Material(vec3(0.0f, 1.0f, 0.0f))
});

// Sfera ciano
spheres.push_back({
    vec3(2.5f, 1.0f, 0.0f), 1.0f,
    Material(vec3(0.0f, 0.5f, 0.5f))
});

// Sfera blu
spheres.push_back({
    vec3(5.0f, 1.0f, 0.0f), 1.0f,
    Material(vec3(0.0f, 0.0f, 1.0f))
});
```

Questo creerà una fila orizzontale di 5 sfere colorate (rossa, gialla, verde, ciano e blu) allineate sull'asse X, tutte alla stessa altezza (y=1) e profondità (z=0).
Ogni sfera ha un raggio di 1 e nessuna riflessione, emissione o trasparenza.

possiamo vederer il primo render 01render.png

## spiegazione del codice

Il nostro shader ha il compito di calcolare il colore che deve avere ogni pixel. Per farlo, ogni pixel lancia dei molteplici raggi che interagiscono con l'ambiente.

    for(int i = 0; i < samplesPerFrame; i++) {
        color += Trace(ray, spheres, state);
    }
    color /= float(samplesPerFrame);

la funzione `Trace` segue il percorso di un raggio attraverso la scena, calcolando l'interazione con gli oggetti e restituendo il colore finale del raggio.

1 calcosa se il raggio interseca con una sfera HitInfo hit = RayCollision(ray, spheres); 
2 se non interseca con nessuna sfera ritorna il colore di sfondo
3 se interseca con una sfera salviamo i dati dell'intersezione in hit
4 calcoliamo il colore della sfera in base al materiale
5 calcoliamo la direzione del raggio riflesso
in cuesto casso essendo una sferra difusione quindi il raggio riflessso sarà casuale


### Aggiunta di riflessione

ora a ogni sfera aggiungiamo la riflessione

dobiame capire come impostare un materiale 
Material(vec3(1.0f, 0.0f, 0.0f), vec3(0.0f, 0.0f, 0.0f), 0.0f, 0.0f, 1.0f, 0.0f)
1. albedo: colore diffuso
2. emissione: colore
3. smoothness: rugosità della superficie
4. emissione strength
5. probalita riflessione
6. indice di rifrazione
quindi setiamo la sfera con la riflessione mettendo il smoothness a 1 e la probabilità di riflessione a 1
quindi adando da sinitra verso destra dencrementiamo di riflessione 1 0.75 0.5 0.25 0

otteniamo il render 02render.png

## capimo la diferrenza tra riflessione e probabilità di riflessione

se mettiamo la probabilità di riflessione a 1 e la riflessione a a 1 e poi verso destra dencrementiamo la probabilità di riflessione 1 0.75 0.5 0.25 0

la riflessione è la quantità di luce riflessa dalla superficie, mentre la probabilità di riflessione è la probabilità che un raggio incidente venga riflesso dalla superficie. smoothness e un mix tra il ragio riflessso e il raggio rifratto


### Aggiunta di rifrazione

ora aggiungiamo la rifrazione che e la capacità di un materiale di far passare la luce attraverso di esso 
cioe materiali diofani come il vetro

e l'indice di rifrazione e la velocità della luce nel vuoto diviso per la velocità della luce nel materiale che e l'utimo parametro ora metiamo tutte le shere biange e metiamo una riflesione incrementale da1.25 a 1.5 a 1.75 a 2 a 2.5

otteniamo il render 04render.png

esendo trasparenti possiamo meterci dentro una sfera 
nell render 05render.png la abbiamo messo tutte le sfrere con ir indice di rifrazione a 1.5

la prima la abbiamo colorata di rosso e notiamo che la luce passa attraverso la sfera e la colora di rosso

la seconda la secondo le abbiamo messo una sferra vuota cio ir di 1,0 

la terza la abbiamo messo una sfera con un indice di rifrazione di 1,0 colorata di verde e come se avese la parte interna colorata di verde

la quarta la abbiamo messo una sfera dentro

la quinta la abbiamo messo una sfera reflitente


### Aggiunta di luce emissiva

ora mettiamo solo una sfera con luce emissiva
vec3(1.0f, 1.f, 1.f), vec3(1.0f, 1.0f, 1.0f), 5.0f colore bianco e intensita 5
e disativiamo la luce ambiente uniform bool environmentEnabled = false;

se guarsiamo i render 06render.png vediamo che la luce emessa dalla  e illumina la scena ma e moto noisi il render perche per un pixel ci sono 50 campionamenti e c' una buona probabilità che il nessun raggio colpisca la sfera emissiva cosi rendendo il pixel nero ma quelli intoeno alquni la ganno colpita quindi qusta rene l'immagine molto noisi carateristica del ray tracing, per risolvere questo problema possiamo usare il denoising, che sono vari algoritmi che riducono il rumore in un immagine, uno e saper la poszione della luce e favorire i raggi che vanno verso la luce
io ho implementato spatialFilter che prende i pixel vicini e li media per ridurre il rumore ma aumenta il blur dell'immagine da ira in poi usiamo qello si vede nel render 06_1render.png



### Aggiunta più luce emissiva

ora mettiamo piu luce emissiva e otteniamo il render 07render.png e se mettiamo la terra riflettente otteniamo il render 07_1render.png

## conclusioni
se mettamo tutto insieme oteniamo il render 08render.png e 09render.png