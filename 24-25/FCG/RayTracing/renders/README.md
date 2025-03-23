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
- `albedo`: colore diffuso (vec3, valori tra 0 e 1)
- `specular`: colore speculare (vec3, valori tra 0 e 1)
- `emission`: emissione di luce (vec3, valori tra 0 e 1 per il colore, ma l'intensità può essere maggiore di 1)
- `roughness`: rugosità della superficie (valori tra 0 e 1)
- `metallic`: metallicità (valori tra 0 e 1)
- `ior`: indice di rifrazione (deve essere maggiore di 1 per funzionare correttamente, tipicamente 1.3-2.5)

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

1. Calcola se il raggio interseca con una sfera `HitInfo hit = RayCollision(ray, spheres);` 
2. Se non interseca con nessuna sfera ritorna il colore di sfondo
3. Se interseca con una sfera salviamo i dati dell'intersezione in hit
4. Calcoliamo il colore della sfera in base al materiale
5. Calcoliamo la direzione del raggio riflesso
   In questo caso essendo una sfera diffusiva, il raggio riflesso sarà casuale


### Aggiunta di riflessione

Ora a ogni sfera aggiungiamo la riflessione.

Dobbiamo capire come impostare un materiale:
```
Material(vec3(1.0f, 0.0f, 0.0f), vec3(0.0f, 0.0f, 0.0f), vec3(0.0f, 0.0f, 0.0f), 0.0f, 1.0f, 0.0f)
```

1. albedo: colore diffuso (valori RGB tra 0 e 1)
2. specular: colore speculare (valori RGB tra 0 e 1)
3. emission: colore emissivo (valori RGB tra 0 e 1, ma l'intensità può essere >1)
4. roughness: rugosità della superficie (0 = liscio, 1 = ruvido)
5. metallic: probabilità di riflessione (0 = non metallico, 1 = completamente metallico)
6. ior: indice di rifrazione (deve essere >1, tipicamente 1.3-2.5)

Quindi settiamo la sfera con la riflessione mettendo il roughness a 0 (liscio) e la metallicità a 1 (completamente riflettente).
Andando da sinistra verso destra decrementiamo la metallicità: 1, 0.75, 0.5, 0.25, 0.

Otteniamo il render 02render.png

## Capiamo la differenza tra rugosità e metallicità

Se mettiamo la metallicità a 1 e la rugosità a 0 (superficie liscia) e poi verso destra decrementiamo la metallicità (1, 0.75, 0.5, 0.25, 0), osserviamo come cambia la riflessione.

La rugosità determina quanto è liscia la superficie e quindi quanto è chiara la riflessione. La metallicità invece determina la probabilità che un raggio venga riflesso piuttosto che diffuso dalla superficie. La rugosità crea un mix tra raggio riflesso in modo speculare e raggio riflesso in modo diffuso.


### Aggiunta di rifrazione

Ora aggiungiamo la rifrazione, che è la capacità di un materiale di far passare la luce attraverso di esso, cioè materiali diafani come il vetro.

L'indice di rifrazione (ior) rappresenta la velocità della luce nel vuoto diviso per la velocità della luce nel materiale. Questo è l'ultimo parametro del materiale. L'ior deve essere maggiore di 1 per funzionare correttamente. Esempi tipici:
- Aria: ~1.0
- Acqua: ~1.33
- Vetro: ~1.5-1.7
- Diamante: ~2.4

Ora mettiamo tutte le sfere bianche e impostiamo un indice di rifrazione incrementale: 1.25, 1.5, 1.75, 2.0, 2.5.

Otteniamo il render 04render.png

Essendo trasparenti, possiamo mettere una sfera dentro l'altra.
Nel render 05render.png abbiamo messo tutte le sfere con indice di rifrazione 1.5:

- La prima l'abbiamo colorata di rosso e notiamo che la luce passa attraverso la sfera e si colora di rosso
- Nella seconda abbiamo messo una sfera vuota, cioè con ior di 1.0
- Nella terza abbiamo messo una sfera con un indice di rifrazione di 1.0 colorata di verde, come se avesse la parte interna colorata di verde
- Nella quarta abbiamo messo una sfera dentro un'altra
- Nella quinta abbiamo messo una sfera riflettente


### Aggiunta di luce emissiva

Ora mettiamo solo una sfera con luce emissiva:
```
Material(vec3(1.0f, 1.f, 1.f), vec3(0.0f, 0.0f, 0.0f), vec3(1.0f, 1.0f, 1.0f), 0.0f, 0.0f, 0.0f, 5.0f)
```
Con colore bianco e intensità 5 (notare che per l'emissione l'intensità può superare 1).
Disattiviamo anche la luce ambiente: `uniform bool environmentEnabled = false;`

Se guardiamo il render 06render.png vediamo che la luce emessa illumina la scena, ma il render è molto rumoroso perché per un pixel ci sono 50 campionamenti e c'è una buona probabilità che nessun raggio colpisca la sfera emissiva, rendendo il pixel nero. Invece i pixel intorno hanno colpito la sfera, rendendo l'immagine molto rumorosa, caratteristica del ray tracing. Per risolvere questo problema possiamo usare il denoising, che comprende vari algoritmi per ridurre il rumore in un'immagine. Un approccio è conoscere la posizione della luce e favorire i raggi che vanno verso di essa.

Ho implementato spatialFilter che prende i pixel vicini e li media per ridurre il rumore, anche se ciò aumenta il blur dell'immagine. Da qui in poi usiamo questo filtro, come si vede nel render 06_1render.png.


### Aggiunta di più luci emissive

Ora mettiamo più luci emissive e otteniamo il render 07render.png. Se rendiamo il terreno riflettente otteniamo il render 07_1render.png.

## Conclusioni
Combinando tutti questi elementi otteniamo i render 08render.png e 09render.png.