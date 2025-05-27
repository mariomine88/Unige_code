# Setup del Renderer

Questo documento illustra i passaggi necessari per configurare una scena 3D, inclusi la telecamera, gli oggetti e i materiali, utilizzando un approccio basato su ray tracing.

## Configurazione della Telecamera

Per impostare correttamente la telecamera negli shader, definire i seguenti parametri:
- **Posizione (`lookfrom`)**: `vec3(0, 1, 6)` (posizione iniziale della telecamera).
- **Punto di interesse (`lookat`)**: `vec3(0, 1, 0)` (centro della scena).
- **Campo visivo (`cameraFov`)**: `70` gradi (angolo di visuale predefinito).

## Configurazione della Scena

La scena viene costruita tramite codice C++, dove le sfere sono organizzate in un array. Ogni sfera è definita da:
1. **Posizione** (`vec3`).
2. **Raggio** (dimensione).
3. **Materiale** (proprietà ottiche).

### Parametri del Materiale
Ogni materiale include le seguenti proprietà in ordine:
- **Albedo**: Colore diffuso (`vec3`, valori tra 0 e 1).
- **Colore Emissione**:  Colore Luce emessa (`vec3`, colore tra 0-1,).
- **intensità Emissioni**: intensità Luce emessa ( intensità può superare 1).
- **smoothness**: Rugosità della superficie (1 = liscio, 0 = ruvido).
- **Metallic**: Metallicità (0 = non metallico, 1 = totalmente riflettente).
- **IOR** (Indice di Rifrazione): Valore tipico tra 1.3 e 2.5 (deve essere >1).
- **Assorbimento della luce**: Colore che assorbe la luce (valori tra 0 e 1).


### Esempio: Terreno
Una sfera di raggio elevato simula un terreno:
```cpp
spheres[0] = Sphere(vec3(0,-1000,0), 1000.0, 
        Material(vec3(0.5), vec3(0), 0.0, 0.0, 0.0, 0.0 , vec3(0.0, 0.0, 0.0)));
    

### Aggiunta di sfere colorate

Per creare una scena più interessante, possiamo aggiungere una serie di sfere colorate disposte in fila. Ecco un esempio di come creare cinque sfere con colori diversi:

```cpp
// Aggiungiamo una fila di sfere colorate

//red
spheres[1] = Sphere(vec3(-5,1,0), 1.0, 
    Material(vec3(1,0,0), vec3(0), 0.0, 0.0, 0.0, 0.0,vec3(0.0)));

// Yellow 
spheres[2] = Sphere(vec3(-2.5,1,0), 1.0, 
    Material(vec3(0.5,0.5,0), vec3(0), 0.0, 0.0, 0.0, 0.0,vec3(0.0)));

// Green
spheres[3] = Sphere(vec3(0,1,0), 1.0, 
    Material(vec3(0,1,0), vec3(0), 10.0, 0.0, 0.0, 0.0,vec3(0.0)));

// Cyan
spheres[4] = Sphere(vec3(2.5,1,0), 1.0, 
    Material(vec3(0,0.5,0.5), vec3(0), 0.0, 0.0, 0.0, 0.0,vec3(0.0)));

// Blue
spheres[5] = Sphere(vec3(5,1,0), 1.0, 
    Material(vec3(0,0,1), vec3(0), 0.0, 0.0, 0.0, 0.0,vec3(0.0)));
```

Questo creerà una fila orizzontale di 5 sfere colorate (rossa, gialla, verde, ciano e blu) allineate sull'asse X, tutte alla stessa altezza (y=1) e profondità (z=0).
Ogni sfera ha un raggio di 1 e nessuna riflessione, emissione o trasparenza.

possiamo vederer il primo render 01render.png

## spiegazione del codice

Lo shader calcola il colore di ogni pixel lanciando multipli raggi e mediando i risultati:


la funzione `Trace` segue il percorso di un raggio attraverso la scena, calcolando l'interazione con gli oggetti e restituendo il colore finale del raggio.

1. Calcola se il raggio interseca con una sfera `HitInfo hit = RayCollision(ray, spheres);` 
2. Se non interseca con nessuna sfera ritorna il colore di sfondo
3. Se interseca con una sfera salviamo i dati dell'intersezione in hit
4. Calcoliamo il colore della sfera in base al materiale
5. Calcoliamo la direzione del raggio riflesso
   In questo caso essendo una sfera diffusiva, il raggio riflesso sarà casuale


### Aggiunta di riflessione

Ora a ogni sfera aggiungiamo la riflessione.

```cpp
// Aggiungiamo una riflessione a ogni sfera
Material(vec3(1.0f, 1.0f, 1.0f), vec3(0.0f, 0.0f, 0.0f), 0.0f,1.0f 1.0f, 0.0f)
```

Quindi settiamo la sfera con la riflessione, mettendo il Metallic a 1.
Andando da sinistra verso destra decrementiamo la smoothness: 1, 0.75, 0.5, 0.25, 0.

Otteniamo il render 02render.png

## Capiamo la differenza tra rugosità e metallicità

Se mettiamo la smoothness a 1 (superficie liscia) a tutte le sfere.
Andando da sinistra verso destra decrementiamo la Metallic: 1, 0.75, 0.5, 0.25, 0.

Otteniamo il render 03render.png

La smoothness determina quanto è liscia la superficie e quindi quanto è chiara la riflessione. 
La smoothness crea un mix tra raggio riflesso in modo speculare e raggio riflesso in modo diffuso.

La metallicità invece determina la probabilità che un raggio venga riflesso perfetamente  dalla superficie. 
la metallicità sceglie se il raggio riflesso sarà speculare o diffuso.


### Aggiunta di rifrazione

Ora aggiungiamo la rifrazione, che è la capacità di un materiale di far passare la luce attraverso di esso, cioè materiali dielettrici.

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
```cpp
Material(vec3(1.000,1.000,1.000), vec3(1.000,1.000,1.000), 10.0, 0.5, 1.0, 0.0,vec3(0.0))
```
Con colore bianco e intensità 10 (notare che per l'emissione l'intensità può superare 1).
Disattiviamo anche la luce ambiente: `bool environmentLight = false;`

Se guardiamo il render 06render.png vediamo che la luce emessa illumina la scena, ma il render è molto rumoroso perché per un pixel ci sono solo 50 campionamenti e c'è una buona probabilità che nessun raggio colpisca la sfera emissiva, rendendo il pixel nero. Invece i pixel intorno hanno colpito la sfera, rendendo l'immagine molto rumorosa, caratteristica del ray tracing. Per risolvere questo problema possiamo usare vari metodi di denoising, che comprende vari algoritmi per ridurre il rumore in un'immagine. 
Come icrementare il numero di campionamenti per pixel, ma questo aumenta il tempo di rendering.
O con l'accumulo di più immagini, ma questo richiede più tempo e memoria, rendendoli inpraticatico per immagini in tempo reale.
Un approccio è conoscere la posizione della luce e favorire i raggi che vanno verso di essa.
alti come spatialFilter che prende i pixel vicini e li media per ridurre il rumore, anche se ciò aumenta il blur dell'immagine. 

### Aggiunta di più luci emissive

Ora mettiamo più luci emissive e otteniamo il render 07render.png. Se rendiamo il terreno riflettente otteniamo il render 07_1render.png.

## Conclusioni
Combinando tutti questi elementi otteniamo i render 08render.png e 09render.png e 10render.png.
