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
#define maxDepth 50

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

// Add these uniforms at the top of your shader
bool environmentEnabled = true;
vec3 skyColorHorizon = vec3(0.7, 0.8, 1.0); 
vec3 skyColorZenith = vec3(0.3, 0.5, 0.8);
vec3 groundColor = vec3(0.4, 0.3, 0.2);
vec3 sunDirection = vec3(0.0, 0.7, -0.7); // Equivalent to _WorldSpaceLightPos0
float sunFocus = 128.0;
float sunIntensity = 1.0;

vec3 GetEnvironmentLight(Ray ray) {
    if (!environmentEnabled) {
        return vec3(0.0);
    }
    // old one 
            /*if (hitIndex == -1) {
            // Apply background color with accumulated throughput
            float t = (uv.y + 1.0) * 0.5;
            vec3 HitColor = mix(vec3(1.0, 1.0, 1.0), vec3(0.5, 0.7, 1.0), t);
            color += throughput*1.1 * HitColor;
            break;
        }
        */
    // Calculate sky gradient
    float skyGradientT = pow(smoothstep(0.0, 0.4, ray.direction.y), 0.35);
    float groundToSkyT = smoothstep(-0.01, 0.0, ray.direction.y);
    vec3 skyGradient = mix(skyColorHorizon, skyColorZenith, skyGradientT);
    float sun = pow(max(0.0, dot(ray.direction, normalize(sunDirection))), sunFocus) * sunIntensity;
    
    // Combine ground, sky, and sun
    vec3 composite = mix(groundColor, skyGradient, groundToSkyT) + sun * float(groundToSkyT >= 1.0);
    return composite;
}

float rand(vec2 co) {
    return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
}

// Random unit vector
vec3 randomUnitVector(vec2 seed) {
    return normalize(vec3(rand(seed) * 2.0 - 1.0,
        rand(seed + vec2(1.0, 2.0)) * 2.0 - 1.0,
        rand(seed + vec2(3.0, 4.0)) * 2.0 - 1.0));
}

// Simpler version for random hemisphere direction
vec3 randomHemisphereDirection(vec3 normal, vec2 seed) {
    // Create a random direction
    vec3 randVec = randomUnitVector(seed);
    
    // Normalize and ensure it's in the correct hemisphere
    if (dot(randVec, normal) < 0.0) {
        randVec = -randVec;
    }
    
    return normalize(randVec + randomUnitVector(seed));
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
    vec3 center; // Fixed to match the usage in intersectSphere
    float radius;
    RayTracingMaterial material;
};

// Ray-sphere intersection function
//quewsta funzione calcola l'intersezione tra un raggio e una sfera 
//cioè calcola la distanza tra il punto di origine del raggio e il punto di intersezione con la sfera
float intersectSphere(Ray ray, Sphere sphere) {
    // Using sphere.center property to match struct definition
    vec3 oc = sphere.center - ray.origin;
    float a = dot(ray.direction, ray.direction);
    float h = dot(oc, ray.direction);
    float c = dot(oc,oc) - sphere.radius * sphere.radius;
    float discriminant = h*h - a*c;
    
    if (discriminant < 0.0) {
        return -1.0;
    } else {
        return (h - sqrt(discriminant)) / a;
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

vec3 Trace(Ray ray, Sphere Sphere[MAX_SPHERES] , vec2 seed) {
    vec3 incominglight = vec3(0.0);
    vec3 rayColor = vec3(1.0);

    for (int depth = 0; depth <= maxDepth; depth++) {
        HitInfo hit = RayCollision(ray, Sphere);
        
        if (hit.hit) {
            ray.origin = hit.hitPoint + hit.normal * 0.0001;
            ray.direction = randomHemisphereDirection(hit.normal, seed);

            RayTracingMaterial material = hit.material;
            vec3 emmitedLight = material.emissionColour * material.emissionStrength;
            incominglight += rayColor * emmitedLight;
            rayColor *= material.colour;
        }else{
            incominglight = GetEnvironmentLight(ray);
            incominglight = vec3(0.0);
        }
    }
    return incominglight;
}


void main() {
    vec2 uv = (gl_FragCoord.xy * 2.0 - resolution.xy) / resolution.y;

    vec3 RO = vec3(0.0, 0.0, 0.0); // Ray Origin
    vec3 RD = normalize(vec3(uv, -1.0)); // Ray Direction
    Ray ray = Ray(RO, RD);


    Sphere sphere[MAX_SPHERES];
    for (int i = 0; i < MAX_SPHERES; i++) {
        sphere[i] = Sphere(sphereCenters[i], sphereRadii[i], RayTracingMaterial(sphereColors[i], sphereEmissionColors[i], sphereSpecularColors[i], sphereEmissionStrengths[i], sphereSmoothness[i], sphereSpecularProbs[i]));
    }

    int rayperpixel = 5;
    vec3 color;

    for (int i = 0; i <= rayperpixel; i++) {
        vec2 seed = uv * (randomN + time * 3545 + i);
        color =+ Trace(ray, sphere, seed); /*
        color = pow(color, vec3(1.0 / 2));
        vec3 accumulatedColor = texelFetch(accumulatedTex, ivec2(gl_FragCoord.xy), 0).rgb;
        vec3 finalColor = mix(accumulatedColor, color, 1.0 / (frameCount + 1.0));
        FragColor = vec4(finalColor, 1.0);
        */
    }

    color /= float(rayperpixel);

    //gamma correction
    color = pow(color, vec3(1.0/2));

    // multiple importance sampling
    float a = 1.0 / (frameCount + 1.0);
    ivec2 fragCoord = ivec2(gl_FragCoord.xy);
    vec3 accumulatedColor = texelFetch(accumulatedTex, fragCoord, 0).rgb;
    vec3 finalColor = mix(accumulatedColor, color, a);

    FragColor = vec4(finalColor, 1.0);
}