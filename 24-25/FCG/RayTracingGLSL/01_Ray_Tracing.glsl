#version 300 es

precision highp float;
uniform vec2 u_resolution;
out vec4 fragColor;

// Ray structure: origin and direction
struct Ray {
    vec3 ori;
    vec3 dir; 
};

// Material properties
struct Material {
    vec3 colour;
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

// Scene setup: one red sphere
const int numSpheres = 1;
Sphere spheres[numSpheres] = Sphere[](
    Sphere(vec3(0.0, 1.0, 0.0), 1.0, Material(vec3(0.8, 0.2, 0.2)))
);

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
    vec3 skyColorHorizon = vec3(0.2, 0.5, 1.0); // Light blue
    vec3 skyColorZenith = vec3(0.1, 0.2, 0.5);  // Dark blue
    
    return mix(skyColorHorizon, skyColorZenith, ray.dir.y);
}

// Main ray tracing function
vec3 Trace(Ray ray) {
    vec3 incomingLight = vec3(0.0);

    HitInfo hit = RayCollision(ray, spheres);
    if (hit.hit){
        incomingLight = hit.material.colour; // Object color
    } else {
        incomingLight = GetEnvironmentLight(ray); // Sky color
    }
    return incomingLight;
}

// Fragment shader entry point
void main()
{
    // Convert screen coordinates to normalized device coordinates
    vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / u_resolution.y;

    // Create camera ray
    Ray ray;
    ray.ori = vec3(0.0, 0.0, 5.0); // Camera position
    ray.dir = normalize(vec3(uv, -1.0)); // Ray direction

    // Trace ray and output color
    fragColor = vec4(Trace(ray),1.0f);
}