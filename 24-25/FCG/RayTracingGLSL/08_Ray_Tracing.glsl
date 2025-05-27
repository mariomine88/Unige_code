#version 300 es

precision highp float;
out vec4 fragColor;
uniform vec2 u_resolution;
uniform float u_time;

int maxDepth = 10;
int samplesPerPixel = 50; // increse for better quality but slower performance 
bool environmentLight = false; // Enable or disable environment light

// Ray structure: origin and direction
struct Ray {
    vec3 ori;
    vec3 dir; 
};

// Material properties
struct Material {
    vec3 colour;
    vec3 emissionColour;
    float emissionStrength;
    float smoothness; // Controls surface roughness: 0.0 = rough/diffuse, 1.0 = mirror-like
    float specularProbability; // Probability of specular reflection (0.0 to 1.0)
};


// Sphere object with position, size and material
struct Sphere {
    vec3 center;
    float radius;
    Material material;
};

// Information about ray-object intersection
struct HitInfo {
    bool hit;
    float dst;
    vec3 hitPoint;
    vec3 normal;
    Material material;
};

// Scene setup: 
const int numSpheres = 2;
Sphere spheres[numSpheres] = Sphere[](
    Sphere(vec3(0.0, 1.0, 0.0), 1.0, Material(vec3(0.8, 0.2, 0.2) , vec3(0.84f, 0.83f, 0.02f), 10.0 ,0.0 ,0.0)),
    Sphere(vec3(0.0, -1000.0, 0.0), 1000.0, Material(vec3(0.3725, 0.2902, 0.0745), vec3(0.0), 0.0 ,1.5, .8))
);

// PCG Random Number Generator
uint pcg_hash(inout uint state) {
    state = state * 747796405u + 2891336453u;
    uint word = ((state >> ((state >> 28u) + 4u)) ^ state) * 277803737u;
    return (word >> 22u) ^ word;
}

// Random number functions from 0 to 1
float randomValue(inout uint state) {
    return float(pcg_hash(state)) / 4294967295.0;
}

// Generate a random unit vector 
vec3 randomUnitVector(inout uint state) {
    // Generate random point in unit sphere using rejection sampling
    vec3 p;
    do {
        p = 2.0 * vec3(randomValue(state), randomValue(state), randomValue(state)) - 1.0;
    } while (dot(p, p) >= 1.0);
    
    return normalize(p);
}

// Calculate ray-sphere intersection using quadratic formula
float intersectSphere(Ray ray, Sphere sphere) {
    vec3 oc = ray.ori - sphere.center;
    float a = dot(ray.dir, ray.dir);
    float b = 2.0 * dot(oc, ray.dir);
    float c = dot(oc, oc) - sphere.radius * sphere.radius;
    float discriminant = b * b - 4.0 * a * c;
    
    if(discriminant < 0.0) return -1.0; // No intersection
    return (-b - sqrt(discriminant)) / (2.0 * a); // Return closest hit
}

// Test ray against all spheres in scene
HitInfo RayCollision(Ray ray, Sphere spheres[numSpheres]) {
    HitInfo hit;
    hit.hit = false;
    hit.dst = 1e30; // Start with very large distance

    // Check each sphere
    for(int i = 0; i < numSpheres; i++) {
        float t = intersectSphere(ray, spheres[i]);
        if(t > 0.00001 && t < hit.dst) { // Valid hit and closer than previous
            hit.hit = true;
            hit.dst = t;
            hit.hitPoint = ray.ori + t * ray.dir;
            hit.normal = normalize(hit.hitPoint - spheres[i].center);
            hit.material = spheres[i].material;
        }
    }
    return hit;
}

// Simple sky gradient for background
vec3 GetEnvironmentLight(Ray ray) {
    if (!environmentLight) return vec3(0.0); // Return black if environment light is disabled
    vec3 skyColorHorizon = vec3(0.24f, 0.35f, 0.62f); 
    vec3 skyColorZenith = vec3(0.6f, 0.63f, 0.71f);  
    
    return mix(skyColorHorizon, skyColorZenith, ray.dir.y);
}

// Main ray tracing function
vec3 Trace(Ray ray,inout uint state) {
    vec3 incomingLight = vec3(0.0);
    vec3 rayColor = vec3(1.0f);

    for (int depth = 0; depth < maxDepth; depth++) {
        // Check for intersection with scene objects
        HitInfo hit = RayCollision(ray, spheres);
        if(!hit.hit) {
            incomingLight += rayColor * GetEnvironmentLight(ray);
            break;
        }
        Material mat = hit.material;
        //Calculate ray directions
        vec3 diffuseDir = normalize(hit.normal + randomUnitVector(state));
        vec3 specularDir = reflect(ray.dir, hit.normal);

        bool isSpecularBounce = mat.specularProbability >= randomValue(state);
        ray.dir = normalize(mix(diffuseDir, specularDir, mat.smoothness * float(isSpecularBounce)));
        rayColor *= (isSpecularBounce) ? mat.colour : vec3(1.0); // Apply color only for diffuse bounces
        ray.ori = hit.hitPoint + hit.normal * 0.0001; // Offset to avoid self-intersection

        // Accumulate light from the hit point
        incomingLight += rayColor * mat.emissionColour * mat.emissionStrength;
        // Calculate color based on material and normal
        rayColor *= mat.colour;
    }

    return incomingLight; 
}


void main() {
    // Convert screen coordinates to normalized device coordinates
    vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / u_resolution.y;

    vec3 lookfrom = vec3(0.0, 1.0, 2.0); // Camera position
    vec3 direction = normalize(vec3(uv, -1.0)); // Ray direction

    // Initialize random state for ray tracing
    uint state = uint(u_time) * 1000u + uint(gl_FragCoord.x) * 1973u + uint(gl_FragCoord.y) * 9277u;

    vec3 color = vec3(0.0);
    // Perform multiple samples per pixel for anti-aliasing and soft shadows
    for (int index = 0; index < samplesPerPixel; ++index) {
        // Apply a small random offset to the ray for anti-aliasing
        vec3 offset = 0.007 * cross(direction, randomUnitVector(state));
        
        // Create a ray from camera position with slightly offset direction
        Ray ray = Ray(lookfrom + offset, direction);
        
        // Accumulate path traced color and average across samples
        color += Trace(ray, state) / float(samplesPerPixel);
    }

    // Apply gamma correction
    color = pow(color, vec3(1.0/2.2)); 
    // Output final color
    fragColor = vec4(color,1.0f);
}