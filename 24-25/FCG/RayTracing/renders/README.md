## Set up

Per fare un render dobbiamo fare il setup, dobbiamo settare la telecamera e la scena.

### Configurazione della telecamera

Per la telecamera nelle shader dobbiamo impostare:
- `lookfrom`: la posizione della telecamera che metteremo a `vec3(0, 1, 5)`
- `lookat`: la coordinata che guarda sarà al centro del render che mettiamo a `vec3(0, 1, 0)`
- `cameraFov`: l'angolo di visuale che lasceremo sempre a 90 gradi

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
    Material(vec3(0.5f, 0.5f, 0.5f), vec3(0, 0, 0), vec3(0, 0, 0), 0.0f, 0.0f, 0.0f, 0.0f)
});
```

### Aggiunta di sfere colorate

Per creare una scena più interessante, possiamo aggiungere una serie di sfere colorate disposte in fila. Ecco un esempio di come creare cinque sfere con colori dell'arcobaleno:

```cpp
// Aggiungiamo una fila di sfere colorate
// Sfera rossa
spheres.push_back({
    vec3(-5.0f, 1.0f, 0.0f), 1.0f,
    Material(vec3(1.0f, 0.0f, 0.0f), vec3(0, 0, 0), vec3(0, 0, 0), 0.0f, 0.0f, 0.0f, 0.0f)
});

// Sfera gialla
spheres.push_back({
    vec3(-2.5f, 1.0f, 0.0f), 1.0f,
    Material(vec3(0.5f, 0.5f, 0.0f), vec3(0, 0, 0), vec3(0, 0, 0), 0.0f, 0.0f, 0.0f, 0.0f)
});

// Sfera verde
spheres.push_back({
    vec3(0.0f, 1.0f, 0.0f), 1.0f,
    Material(vec3(0.0f, 1.0f, 0.0f), vec3(0, 0, 0), vec3(0, 0, 0), 0.0f, 0.0f, 0.0f, 0.0f)
});

// Sfera ciano
spheres.push_back({
    vec3(2.5f, 1.0f, 0.0f), 1.0f,
    Material(vec3(0.0f, 0.5f, 0.5f), vec3(0, 0, 0), vec3(0, 0, 0), 0.0f, 0.0f, 0.0f, 0.0f)
});

// Sfera blu
spheres.push_back({
    vec3(5.0f, 1.0f, 0.0f), 1.0f,
    Material(vec3(0.0f, 0.0f, 1.0f), vec3(0, 0, 0), vec3(0, 0, 0), 0.0f, 0.0f, 0.0f, 0.0f)
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