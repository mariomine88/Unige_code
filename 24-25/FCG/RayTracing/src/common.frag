//parameter you can modifie
float cameraFov = 70.0; // Field of view in degrees
vec3 lookfrom = vec3(0, 1, 6);   // Point camera is looking from
vec3 lookat = vec3(0, 1 , 0);  // Point camera is looking at

#define MAX_DEPTH 10
#define SAMPLES_PER_FRAME 10
#define MAX_SPHERES 30

#define PI 3.14159265359 /

struct Material {
    vec3 colour;
    vec3 emission;
    float emissionStrength;
    float smoothness;
    float specularProb;
    float ir;
    vec3  refractionColor; 
};

struct Sphere {
    vec3 center;
    float radius;
    Material mat;
};

struct Ray {
    vec3 origin;
    vec3 direction;
};

struct HitInfo {
    bool hit;
    float dst;
    vec3 point;
    vec3 normal;
    bool inside;
    Material mat;
};

Sphere spheres[MAX_SPHERES];

//funzion to set up word
void initSpheres() {
    // Ground
    spheres[0] = Sphere(vec3(0,-1000,0), 1000.0, Material(vec3(0.5), vec3(0), 0.0, 0.0, 0.0, 0.0 ,vec3(0)));
    
    //red
    spheres[1] = Sphere(vec3(-5,1,0), 1.0, 
    Material(vec3(1,0,0), vec3(0), 0.0, 0.0, 0.0, 0.0,vec3(0)));
        
    // Yellow
    spheres[2] = Sphere(vec3(-2.5,1,0), 1.0, 
        Material(vec3(0.5,0.5,0), vec3(0), 0.0, 1.0, 1.0, 0.0,vec3(0)));
    // Green
    spheres[3] = Sphere(vec3(0,1,0), 1.0, 
        Material(vec3(0,1,0), vec3(0,1,0), 10.0, 0.0, 0.0, 0.0,vec3(0)));
    // Cyan
    spheres[4] = Sphere(vec3(2.5,1,0), 1.0, 
        Material(vec3(1.000,1.000,1.000), vec3(0), 0.0, 0.0, 0.0, 2.0,vec3(1.000,0.000,0.000)));
    // Blue
    spheres[5] = Sphere(vec3(5,1,0), 1.0, 
        Material(vec3(0,0,1), vec3(0), 0.0, 0.0, 0.0, 0.0,vec3(0)));
}

// PCG Random Number Generator
uint hash(inout uint state) {
    state = state * 747796405u + 2891336453u;
    uint word = ((state >> ((state >> 28u) + 4u)) ^ state) * 277803737u;
    return (word >> 22u) ^ word;
}

float rand(inout uint state) {
    return float(hash(state)) / 4294967295.0;
}

// Random value in normal distribution (with mean=0 and sd=1)
float randomValueNormalDistribution(inout uint state){
    float theta = 2.0 * 3.1415926 * rand(state);
	float rho = sqrt(-2.0 * log(rand(state)));
	return rho * cos(theta);
}

vec3 randomUnitVector(inout uint state) {
    return normalize(vec3(randomValueNormalDistribution(state), randomValueNormalDistribution(state), randomValueNormalDistribution(state)));
} 

float intersect(Ray ray, Sphere s) {
    vec3 oc = ray.origin - s.center;
    float a = dot(ray.direction, ray.direction);
    float b = 2.0 * dot(oc, ray.direction);
    float c = dot(oc, oc) - s.radius * s.radius;
    float discriminant = b * b - 4.0 * a * c;
    if(discriminant < 0.0) return -1.0;
    
    return (-b - sqrt(discriminant)) / (2.0 * a);
}