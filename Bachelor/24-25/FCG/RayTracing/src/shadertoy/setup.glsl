//parameter you can modifie
float cameraFov = 70.0; // Field of view in degrees
vec3 lookfrom = vec3(0, 1, 6);   // Point camera is looking from
vec3 lookat = vec3(0, 1 , 0);  // Point camera is looking at

// Ray tracing configuration
#define MAX_DEPTH 10         // Maximum number of ray bounces
#define SAMPLES_PER_FRAME 10 // Samples per pixel each frame
#define MAX_SPHERES 30       // Maximum number of spheres in the scene

bool environmentLight = true; // Enable or disable environment light


struct Material {
    vec3 colour;             // Diffuse color (albedo)
    vec3 emissionColour;           // Emission color for light sources
    float emissionStrength;  // Brightness multiplier for emission
    float smoothness;        // Controls material smoothness (0-1)
    float specularProbability;      // Probability of specular reflection (0-1)
    float ir;                // Index of refraction (1.0 < non-refractive)
    vec3 absorptionColour;   // Absorption color for transparent materials 
};

struct Sphere {
    vec3 center;
    float radius;
    Material material;
};


Sphere spheres[MAX_SPHERES];

//funzion to set up word
void initSpheres() {
    // Ground
    spheres[0] = Sphere(vec3(0,-1000,0), 1000.0, 
        Material(vec3(0.5), vec3(0), 0.0, 0.0, 0.0, 0.0 , vec3(0.0, 0.0, 0.0)));
    
    
    //red
    spheres[1] = Sphere(vec3(-5,1,0), 1.0, 
        Material(vec3(1,0,0), vec3(0), 0.0, 0.0, 0.0, 0.0,vec3(0.0, 0.0, 0.0)));
    // Yellow reflecting
    spheres[2] = Sphere(vec3(-2.5,1,0), 1.0, 
        Material(vec3(0.5,0.5,0), vec3(0), 0.0, 1.0, 1.0, 0.0,vec3(0.0, 0.0, 0.0)));
    // Green light
    spheres[3] = Sphere(vec3(0,1,0), 1.0, 
        Material(vec3(0,1,0), vec3(0,1,0), 10.0, 0.0, 0.0, 0.0,vec3(0.0, 0.0, 0.0)));
    // Cyan glass
    spheres[4] = Sphere(vec3(2.5,1,0), 1.0, 
        Material(vec3(0,1,1), vec3(0), 0.0, 0.1, 0.0, 1.5,vec3(0.0, 0.0, 0.0)));
    // Blue
    spheres[5] = Sphere(vec3(5,1,0), 1.0, 
        Material(vec3(0,0,1), vec3(0), 0.0, .5, 1.0, 0.0,vec3(0.0, 0.0, 0.0)));
}