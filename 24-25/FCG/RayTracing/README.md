## Shadeer di Ray Tracer 

Un'implementazione di ray tracing in SFML in glsl e shadertoy.

# Ray Tracer code
nella cartella scr ci sono i 10 passaggi per realizzare un ray tracer in GLSL.
La versione completa è su [shadertoy](https://www.shadertoy.com/view/tXXGDj) , 
poiche per avvere la migliore qualita si deve usare l'acculamento di shader che non è possibile fare in glsl puro.

Per ottenere rendering fisicamente accurati, dobbiamo simulare il comportamento della luce.
La migliore aprosimazione atuale e creare dei raggi luminosi e seguendo il loro percorso
attraverso la scena (ray tracing).

## introduzione all codice

sono partrito dall codice esempio di multiple.glsl che ho modificato per creare un il mio ray tracer.

Il nostro shader ha il compito di calcolare il colore che deve avere ogni pixel. Per farlo, ogni pixel lancia dei molteplici raggi che interagiscono con l'ambiente. 
Facendone la media dei campioni, determiniamo il colore finale del pixel.

Le interazioni con l'ambiente devono imitare quelle della luce reale, quindi in base al materiale che incontriamo dobbiamo simulare diffusione, riflessione o refrazione.

La mia implementazione include un sistema di materiali basato sulla fisica che comprende:

Riflessione diffusa
Riflessione speculare
Emissione (sorgenti luminose)
smoothness
Metallicità
Indice di rifrazione per materiali trasparenti
assorbimento della luce dai ogetti trasparenti

Gli oggetti della scena sono rappresentati da sfere.

## codice

Per realizzare il ray tracing, il nostro codice utilizza diversi elementi:

Ray: rappresentazione matematica dei raggi luminosi
Sphere: oggetti geometrici della scena
Material: proprietà fisiche delle superfici
HitRecord: informazioni sulle intersezioni raggio-oggetto
Implementiamo anche:

Funzioni per generare numeri casuali per il Path Tracing con campionamento Monte Carlo, per imitare la casualità della luce
Algoritmi di intersezione tra raggi e sfere
Funzione Trace per seguire il percorso della luce nella scena

## Renders

Nella cartella renders sono presenti diversi rendering prodotti in shadertoy, accompagnati da spiegazioni dettagliate. Questi esempi illustrano progressivamente il funzionamento del ray tracer, mostrando le varie caratteristiche implementate come riflessione, rifrazione, emissione luminosa e altri effetti fisici. Le immagini permettono di comprendere visivamente come i concetti teorici vengono applicati nel codice.

## source
https://raytracing.github.io/books/RayTracingInOneWeekend.html
https://blog.demofox.org/2020/05/25/casual-shadertoy-path-tracing-1-basic-camera-diffuse-emissive/
https://youtu.be/Qz0KTGYJtUk?si=Z5etLgMJ3N6XAAhz