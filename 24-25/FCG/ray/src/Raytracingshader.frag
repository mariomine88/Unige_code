#version 420 core
#pragma extension GL_EXT_shader_explicit_arithmetic_types : require

out vec4 FragColor;

uniform float time;
uniform vec2 resolution;
uniform int numSpheres;

uniform sampler2D accumulatedTex;
uniform float frameCount;

uniform int randomN;

// Define maximum number of spheres (must match C++ code)
#define MAX_SPHERES 30
uniform vec3 sphereCenters[MAX_SPHERES];
uniform float sphereRadii[MAX_SPHERES];

// Material properties
uniform vec3 sphereColors[MAX_SPHERES];
uniform vec3 sphereEmissionColors[MAX_SPHERES];
uniform vec3 sphereSpecularColors[MAX_SPHERES];
uniform float sphereEmissionStrengths[MAX_SPHERES];
uniform float sphereSmoothness[MAX_SPHERES];
uniform float sphereSpecularProbs[MAX_SPHERES];

// Variables to track closest intersection
int hitSphereIndex = -1;
#define maxDepth 5  // Reduced from 50 for better performance

// Ray structure
// Ray structure e come quelli di fisica dove l'origine è il punto di partenza e la direzione è la direzione del raggio
// direction è normalizzato cioè la lunghezza è 1
struct Ray {
    vec3 origin;
    vec3 direction;

    // Function to get point at distance t along the ray
    vec3 at(float t) {
        return origin + t * direction;
    }
};

// Environment settings
bool environmentEnabled = true;
vec3 skyColorHorizon = vec3(0.7, 0.8, 1.0); 
vec3 skyColorZenith = vec3(0.3, 0.5, 0.8);
vec3 groundColor = vec3(0.4, 0.3, 0.2);
vec3 sunDirection = vec3(0.0, 0.7, -0.7);
float sunFocus = 128.0;
float sunIntensity = 1.0;

vec3 GetEnvironmentLight(Ray ray) {
    if (!environmentEnabled) {
        return vec3(0.0);
    }
    
    // Calculate sky gradient
    float skyGradientT = pow(smoothstep(0.0, 0.4, ray.direction.y), 0.35);
    float groundToSkyT = smoothstep(-0.01, 0.0, ray.direction.y);
    vec3 skyGradient = mix(skyColorHorizon, skyColorZenith, skyGradientT);
    float sun = pow(max(0.0, dot(ray.direction, normalize(sunDirection))), sunFocus) * sunIntensity;
    
    // Combine ground, sky, and sun
    vec3 composite = mix(groundColor, skyGradient, groundToSkyT) + sun * float(groundToSkyT >= 1.0);
    return composite;
}

// PCG Random Number Generator
// Based on the PCG implementation by Mark Jarzynski and Marc Olano
uint pcg(uint seed) {
    uint state = seed * 747796405u + 2891336453u;
    uint word = ((state >> ((state >> 28u) + 4u)) ^ state) * 277803737u;
    return (word >> 22u) ^ word;
}

float pcgFloat(uvec2 seed) {
    // Combine both parts of the seed
    uint s = pcg(seed.x ^ pcg(seed.y));
    // Convert to float between 0 and 1
    return float(s) / 4294967295.0;
}

// Random unit vector using PCG
vec3 randomUnitVector(vec2 seed) {
    // Use frameCount and randomN to advance the seed
    uvec2 pcgSeed = uvec2(
        floatBitsToUint(seed.x * (randomN + 1u) + time),
        floatBitsToUint(seed.y * (randomN + 2u) + time * 1000.0)
    );
    
    // Generate 3 random values between -1 and 1
    float x = pcgFloat(pcgSeed) * 2.0 - 1.0;
    float y = pcgFloat(pcgSeed + uvec2(16u, 23u)) * 2.0 - 1.0;
    float z = pcgFloat(pcgSeed + uvec2(32u, 45u)) * 2.0 - 1.0;
    
    return normalize(vec3(x, y, z));
}

// Improved hemisphere direction generator
vec3 randomHemisphereDirection(vec3 normal, vec2 seed) {
    vec3 randVec = randomUnitVector(seed);
    
    // Ensure it's in the correct hemisphere
    if (dot(randVec, normal) < 0.0) {
        randVec = -randVec;
    }
    
    // Create a more accurate cosine-weighted distribution
    uvec2 pcgSeed = uvec2(
        floatBitsToUint(seed.x * (randomN + 3u) + time * 2.5),
        floatBitsToUint(seed.y * (randomN + 4u) + time * 3500.0)
    );
    
    float a = pcgFloat(pcgSeed);
    float b = pcgFloat(pcgSeed + uvec2(5u, 7u));
    
    float phi = 2.0 * 3.14159265359 * a;
    float cosTheta = sqrt(1.0 - b);
    float sinTheta = sqrt(b);
    
    // Create coordinate system around normal
    vec3 tangent, bitangent;
    if (abs(normal.x) > abs(normal.y)) {
        tangent = normalize(cross(normal, vec3(0.0, 1.0, 0.0)));
    } else {
        tangent = normalize(cross(normal, vec3(1.0, 0.0, 0.0)));
    }
    bitangent = cross(normal, tangent);
    
    // Construct the direction
    return normalize(
        tangent * cos(phi) * sinTheta +
        bitangent * sin(phi) * sinTheta +
        normal * cosTheta
    );
}

struct RayTracingMaterial {
    vec3 colour;
    vec3 emissionColour;
    vec3 specularColour;
    float emissionStrength;
    float smoothness;
    float specularProbability;
};

struct Sphere {
    vec3 center;
    float radius;
    RayTracingMaterial material;
};

// Ray-sphere intersection function
float intersectSphere(Ray ray, Sphere sphere) {
    vec3 oc = ray.origin - sphere.center;
    float a = dot(ray.direction, ray.direction);
    float h = dot(oc, ray.direction);
    float c = dot(oc, oc) - sphere.radius * sphere.radius;
    float discriminant = h*h - a*c;
    
    if (discriminant < 0.0) {
        return -1.0;
    } else {
        float t = (h - sqrt(discriminant)) / a;
        return (t > 0.0) ? t : -1.0; // Return -1 for intersections behind the ray
    }
}

struct HitInfo {
    bool hit;
    float dst;
    vec3 hitPoint;
    vec3 normal;
    RayTracingMaterial material;
};

HitInfo RayCollision(Ray ray, Sphere Sphere[MAX_SPHERES]) {
    HitInfo hit;
    hit.hit = false;
    hit.dst = 1e30;

    for (int i = 0; i < numSpheres; i++) {
        float t = intersectSphere(ray, Sphere[i]);
        if (t > 0.0 && t < hit.dst) {
            hit.hit = true;
            hit.dst = t;
            hit.hitPoint = ray.at(t);
            hit.normal = normalize(hit.hitPoint - Sphere[i].center);
            hit.material = Sphere[i].material;
        }
    }
    return hit;
}

vec3 Trace(Ray ray, Sphere Sphere[MAX_SPHERES], vec2 seed) {
    vec3 incomingLight = vec3(0.0);
    vec3 rayColor = vec3(1.0);

    for (int depth = 0; depth < maxDepth; depth++) {
        HitInfo hit = RayCollision(ray, Sphere);
        
        if (hit.hit) {
            // Update ray for next bounce
            ray.origin = hit.hitPoint + hit.normal * 0.001;
            
            // Material properties
            RayTracingMaterial material = hit.material;
            vec3 emittedLight = material.emissionColour * material.emissionStrength;
            
            // Russian roulette for material selection
            uvec2 pcgSeed = uvec2(
                floatBitsToUint(seed.x + float(depth) + time * 5.0),
                floatBitsToUint(seed.y + float(depth) * 2.0 + time * 7.0)
            );
            
            float materialSample = pcgFloat(pcgSeed);
            
            // Handle specular reflection
            if (materialSample < material.specularProbability) {
                // Specular reflection
                vec3 reflected = reflect(ray.direction, hit.normal);
                // Add some randomness based on smoothness
                vec3 randomDir = randomUnitVector(seed + vec2(float(depth), float(depth) * 2.0));
                ray.direction = normalize(mix(randomDir, reflected, material.smoothness));
                
                // Update throughput with specular color
                rayColor *= material.specularColour;
            } else {
                // Diffuse reflection
                ray.direction = randomHemisphereDirection(hit.normal, seed + vec2(float(depth) * 3.0, float(depth) * 4.0));
                
                // Update throughput with diffuse color
                rayColor *= material.colour;
            }
            
            // Add emitted light from this surface to accumulated light
            incomingLight += rayColor * emittedLight;
            
            // Russian roulette path termination
            if (depth > 2) {
                float maxComponent = max(max(rayColor.r, rayColor.g), rayColor.b);
                if (pcgFloat(pcgSeed + uvec2(71u, 89u)) > maxComponent) {
                    break; // Terminate path
                }
                // Compensate for termination probability
                rayColor /= maxComponent;
            }
        } else {
            // Ray hit nothing, add environment light and terminate
            incomingLight += rayColor * GetEnvironmentLight(ray);
            break;
        }
    }
    
    return incomingLight;
}

void main() {
    vec2 uv = (gl_FragCoord.xy * 2.0 - resolution.xy) / resolution.y;

    // Create the initial ray
    vec3 RO = vec3(0.0, 0.0, 0.0);
    vec3 RD = normalize(vec3(uv, -1.0));
    Ray ray = Ray(RO, RD);

    // Setup scene objects
    Sphere sphere[MAX_SPHERES];
    for (int i = 0; i < MAX_SPHERES; i++) {
        sphere[i] = Sphere(
            sphereCenters[i], 
            sphereRadii[i], 
            RayTracingMaterial(
                sphereColors[i], 
                sphereEmissionColors[i], 
                sphereSpecularColors[i], 
                sphereEmissionStrengths[i], 
                sphereSmoothness[i], 
                sphereSpecularProbs[i]
            )
        );
    }

    // Multiple samples per pixel for anti-aliasing
    int raysPerPixel = 5;
    vec3 color = vec3(0.0);
    
    for (int i = 0; i < raysPerPixel; i++) {
        vec2 seed = uv * (float(randomN) + time * 3545.0 + float(i));
        color += Trace(ray, sphere, seed); // Fixed += operator (was =+)
    }

    color /= float(raysPerPixel);

    // Gamma correction
    color = pow(color, vec3(1.0/2.2)); // Using 2.2 for standard gamma

    // Progressive accumulation with previous frames
    float a = 1.0 / (frameCount + 1.0);
    ivec2 fragCoord = ivec2(gl_FragCoord.xy);
    vec3 accumulatedColor = texelFetch(accumulatedTex, fragCoord, 0).rgb;
    vec3 finalColor = mix(accumulatedColor, color, a);

    FragColor = vec4(finalColor, 1.0);
}