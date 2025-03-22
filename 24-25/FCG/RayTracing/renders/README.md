## set up

per fare un render dobbiamo fare il setap , dobiamo settare la telecamera e la scenna
per la telecamer nelle shader ha lookfrom che e la psizione della telecamera che meteremo a
vec3(0, 1, 5), lookat la cordinata che guarda ssara al centro del render che mettiamo 
a vec3(0, 1,0); e il cameraFov che lasceremo sempre a 90 m

per il seting della scene dobiamo andare nel c e settare le sfere in u array
metiamo una prima sferra molto grande e grizi che sara il nostro tereno le sferro hanno 3  parametri posizione dimensione e material, materiale ha un sacco di variabili quindi le vediamo con calma     
spheres.push_back({
        vec3(0.0f, -1000.0f, 0.0f), 1000.0f,
        Material(vec3(0.5f, .5f, 0.5f), vec3(0, 0, 0), vec3(0, 0, 0), 0.0f, 0.0f, 0.0f, 0.0f)
});

la prima e colore vec3(0.5f, .5f, 0.5f) e per il momento usaimo quella per crare varie shere colorate 