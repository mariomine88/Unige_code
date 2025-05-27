# Passi di Implementazione del Ray Tracing

Questi sono i passi progressivi per sviluppare un ray tracer shader.

## Step 01: Primo Ray Tracer - Singola Sfera
Iniziamo ristruturando le basi del ray tracing con le strutture dati fondamentali come Ray, Material, Sphere e HitInfo. Solo una sfera rossa contro un gradiente di cielo - niente illuminazione complessa ancora, solo far sì che i raggi colpiscano gli oggetti e restituiscano colori.

## Step 02: Oggetti Multipli
Ora aggiungiamo un piano di terra (in realtà solo una sfera enorme). In più aggiungiamo le funzioni per generare numeri casuali.

## Step 03: Fondamenta del Path Tracing
Ora facciamo che i raggi rimbalzino nella scena fino a 10 volte. Ogni rimbalzo cambia il colore, creando effetti di illuminazione realistici attraverso il campionamento Monte Carlo.

## Step 04: Anti-Aliasing
Aggiungiamo un antialiasing e aggiungiamo anche la correzione gamma per far sembrare giusti i colori sullo schermo.

## Step 05: Materiali Emissivi
Ora implementiamo materiali emissivi che emettono luce, come una lampadina. Aggiungiamo la possibilità di fare il toggle del cielo.

## Step 06: Levigatezza dei Materiali
I materiali diventano più realistici con un parametro di levigatezza che controlla quanto sono specchiati o ruvidi. Il terreno ottiene una levigatezza parziale quindi non è più completamente opaco.

## Step 07: Probabilità Speculare
Aggiunto il controllo della metallicità - i materiali possono scegliere casualmente tra comportamento diffuso e metallico basato sulle loro proprietà. Spegnamo l'illuminazione ambientale per vedere meglio come funzionano le nostre sorgenti luminose.

## Step 08: Materiali di Vetro - Rifrazione Base
Il vetro entra in scena! I materiali ora possono piegare la luce usando la legge di Snell e le equazioni di Fresnel. La nostra nuova sfera di vetro ha un indice di rifrazione di 1.3, facendola sembrare propriamente trasparente.

## Step 09: Illuminazione Ambientale Avanzata
Facciamo un cambiamento alla telecamera: ora ha lookfrom per dire da dove guardare la scena, e lookat per dire dove guardare.

## Step 10: Renderer Fisicamente Basato Completo
Miglioriamo il cielo per renderlo più realistico con un sole e una linea di orizzonte.

## Versione Shadertoy
La versione web aggiunge rendering progressivo - ogni frame si mescola con i precedenti per ridurre il rumore nel tempo.