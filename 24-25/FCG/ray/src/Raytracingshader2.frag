#version 420 core
#pragma extension GL_EXT_shader_explicit_arithmetic_types : require

out vec4 FragColor;

// Uniforms
uniform float time;
uniform vec2 resolution;
uniform int numSpheres;
uniform sampler2D accumulatedTex;
uniform float frameCount;
uniform uint randomN;

#define MAX_SPHERES 30
uniform vec3 sphereCenters[MAX_SPHERES];
uniform float sphereRadii[MAX_SPHERES];
uniform vec3 sphereColors[MAX_SPHERES];
uniform vec3 sphereEmissionColors[MAX_SPHERES];
uniform vec3 sphereSpecularColors[MAX_SPHERES];
uniform float sphereEmissionStrengths[MAX_SPHERES];
uniform float sphereSmoothness[MAX_SPHERES];
uniform float sphereSpecularProbs[MAX_SPHERES];

// Constants
#define maxDepth 100
#define PI 3.14159265358979323846

// Environment settings
uniform bool environmentEnabled = true;
uniform vec3 skyColorHorizon = vec3(0.7, 0.8, 1.0); 
uniform vec3 skyColorZenith = vec3(0.3, 0.5, 0.8);
uniform vec3 groundColor = vec3(0.4, 0.3, 0.2);
uniform vec3 sunDirection = vec3(0.0, 0.7, -0.7);
uniform float sunFocus = 128.0;
uniform float sunIntensity = 1.0;


// Ray tracing structures
struct Ray {
    vec3 origin;
    vec3 direction;

    vec3 at(float t) {
        return origin + t * direction;
    }
};

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

struct HitInfo {
    bool hit;
    float dst;
    vec3 hitPoint;
    vec3 normal;
    RayTracingMaterial material;
};

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

vec3 randomInUnitSphere(inout uint state) {
    vec3 p;
    do {
        p = 2.0 * vec3(randomValue(state), randomValue(state), randomValue(state)) - 1.0;
    } while (dot(p, p) >= 1.0);
    return p;
}

vec3 randomCosineDirection(inout uint state, vec3 normal) {
    // Create orthonormal basis
    vec3 tangent = normalize(cross(abs(normal.x) > 0.1 ? vec3(0,1,0) : vec3(1,0,0), normal));
    vec3 bitangent = cross(normal, tangent);
    
    // Generate cosine-weighted direction
    float r1 = randomValue(state);
    float r2 = randomValue(state);
    float phi = 2.0 * PI * r1;
    
    float x = cos(phi) * sqrt(r2);
    float y = sin(phi) * sqrt(r2);
    float z = sqrt(1.0 - r2);
    
    return normalize(tangent * x + bitangent * y + normal * z);
}

vec3 randomHemisphereDirection(inout uint state, vec3 normal) {
    return normalize(normal + randomInUnitSphere(state));
}

float intersectSphere(Ray ray, Sphere sphere) {
    vec3 oc = ray.origin - sphere.center;
    float a = dot(ray.direction, ray.direction);
    float b = 2.0 * dot(oc, ray.direction);
    float c = dot(oc, oc) - sphere.radius * sphere.radius;
    float discriminant = b * b - 4.0 * a * c;
    
    if(discriminant < 0.0) return -1.0;
    return (-b - sqrt(discriminant)) / (2.0 * a);
}

HitInfo RayCollision(Ray ray, Sphere spheres[MAX_SPHERES]) {
    HitInfo hit;
    hit.hit = false;
    hit.dst = 1e30;

    for(int i = 0; i < numSpheres; i++) {
        float t = intersectSphere(ray, spheres[i]);
        if(t > 0.0 && t < hit.dst) {
            hit.hit = true;
            hit.dst = t;
            hit.hitPoint = ray.at(t);
            hit.normal = normalize(hit.hitPoint - spheres[i].center);
            hit.material = spheres[i].material;
        }
    }
    return hit;
}

vec3 GetEnvironmentLight(Ray ray) {
    if(!environmentEnabled) return vec3(0.0);
    
    float skyGradientT = pow(smoothstep(0.0, 0.4, ray.direction.y), 0.35);
    float groundToSkyT = smoothstep(-0.01, 0.0, ray.direction.y);
    vec3 skyGradient = mix(skyColorHorizon, skyColorZenith, skyGradientT);
    float sun = pow(max(0.0, dot(ray.direction, normalize(sunDirection))), sunFocus) * sunIntensity;
    
    //uncomen for black sky
    //return skyGradient = vec3(0.0);

    return mix(groundColor, skyGradient, groundToSkyT) + sun * float(groundToSkyT >= 1.0);
}

vec3 Trace(Ray ray, Sphere spheres[MAX_SPHERES], inout uint state) {
    vec3 incomingLight = vec3(0.0);
    vec3 throughput = vec3(1.0);

    for(int depth = 0; depth < maxDepth; depth++) {
        HitInfo hit = RayCollision(ray, spheres);
        
        if(!hit.hit) {
            incomingLight += throughput * GetEnvironmentLight(ray);
            break;
        }

        RayTracingMaterial mat = hit.material;
        incomingLight += throughput * mat.emissionColour * mat.emissionStrength;
        
        // Russian Roulette termination
        if(depth > 3) {
            float q = max(0.05, 1.0 - length(throughput));
            if(randomValue(state) < q) break;
            throughput /= 1.0 - q;
        }

        if(randomValue(state) < mat.smoothness) {
            // Specular reflection
            ray.direction = reflect(ray.direction, hit.normal);
        } else {
            // Diffuse reflection with importance sampling
             ray.direction = randomCosineDirection(state, hit.normal);
        }

        ray.origin = hit.hitPoint + hit.normal * 0.0001;
        throughput *= mat.colour;
    }
    
    return incomingLight;
}

vec3 spatialDenoise(ivec2 coord) {
    vec3 sum = vec3(0);
    for(int x = -1; x <= 1; x++) {
        for(int y = -1; y <= 1; y++) {
            sum += texelFetch(accumulatedTex, coord + ivec2(x,y), 0).rgb;
        }
    }
    return sum / 9.0;
}

void main() {
    ivec2 fragCoord = ivec2(gl_FragCoord.xy);
    vec2 uv = (gl_FragCoord.xy * 2.0 - resolution.xy) / resolution.y;
    
    // Initialize PCG state
    uint state = uint(randomN) + 
               uint(fragCoord.x) * 1973u + 
               uint(fragCoord.y) * 9277u + 
               uint(frameCount) * 26699u;

    Ray ray = Ray(vec3(0.0), normalize(vec3(uv, -1.0)));
    Sphere spheres[MAX_SPHERES];
    
    for(int i = 0; i < MAX_SPHERES; i++) {
        spheres[i] = Sphere(
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

    // Temporal accumulation
    const int samplesPerFrame = 50;
    vec3 color = vec3(0.0);
    
    for(int i = 0; i < samplesPerFrame; i++) {
        color += Trace(ray, spheres, state);
    }
    color /= float(samplesPerFrame);

    //color = mix(color, spatialDenoise(fragCoord), 0.5);

    // Gamma correction
    color = pow(color, vec3(1.0/2.2));
    
    // Blend with accumulated result
    vec3 accumulated = texelFetch(accumulatedTex, fragCoord, 0).rgb;
    float a = 1.0 / (frameCount + 1.0 );
    FragColor = vec4(mix(accumulated, color, a), 1.0);
}