#version 420 core
#pragma extension GL_EXT_shader_explicit_arithmetic_types : require

out vec4 FragColor;

// Uniforms
uniform float time;
uniform vec2 resolution;
uniform int numSpheres;
uniform sampler2D accumulatedTex;
uniform int frameCount;
uniform int randomSeed;

#define MAX_SPHERES 30
uniform vec3 sphereCenters[MAX_SPHERES];
uniform float sphereRadii[MAX_SPHERES];
uniform vec3 sphereColors[MAX_SPHERES];
uniform vec3 sphereEmissionColors[MAX_SPHERES];
uniform vec3 sphereSpecularColors[MAX_SPHERES];
uniform float sphereEmissionStrengths[MAX_SPHERES];
uniform float sphereSmoothness[MAX_SPHERES];
uniform float sphereSpecularProbs[MAX_SPHERES];
uniform float sphereIRs[MAX_SPHERES];

// Constants
#define maxDepth 40
#define samplesPerFrame 30
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
    float ir;
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

// Random value in normal distribution (with mean=0 and sd=1)
float RandomValueNormalDistribution(inout uint state){
    float theta = 2 * 3.1415926 * randomValue(state);
	float rho = sqrt(-2 * log(randomValue(state)));
	return rho * cos(theta);
}

vec3 randomInUnitSphere(inout uint state) {
    return normalize(vec3(RandomValueNormalDistribution(state), RandomValueNormalDistribution(state), RandomValueNormalDistribution(state)));
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
        if(t > 0.00001 && t < hit.dst) {
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
    
    return mix(groundColor, skyGradient, groundToSkyT) + sun * float(groundToSkyT >= 1.0);
}

Ray Refract(Ray ray, HitInfo hit, inout uint state) {
    RayTracingMaterial mat = hit.material;
    float eta = mat.ir;
    vec3 normal = hit.normal;

    // Determine if the ray is inside the material
    if (dot(ray.direction, normal) > 0.0) {
        normal = -normal; // Flip normal to face incoming ray
    } else {
        eta = 1.0 / eta; // Adjust eta for entering the material
    }

    // Calculate the refracted direction
    vec3 refracted = refract(ray.direction, normal, eta);

    // Compute cosine of the incidence angle (adjusted for hemisphere)
    float cos_theta = min(abs(dot(normalize(ray.direction), normal)), 1.0);
    // Schlick's approximation for Fresnel reflectance
    float R0 = pow((1.0 - eta) / (1.0 + eta), 2.0);
    float reflectance = R0 + (1.0 - R0) * pow(1.0 - cos_theta, 5.0);

    // Use a random value to decide between reflection and refraction
    float random = randomValue(state); // Assume this generates a random value between 0 and 1

    // Check for total internal reflection or use Schlick's reflectance
    if (refracted == vec3(0.0) || random < reflectance) {
        ray.direction = reflect(ray.direction, normal);
    } else {
    ray.direction = refracted;
    }

    // Adjust the ray origin to prevent self-intersection
    ray.origin = hit.hitPoint - normal * 0.0001;
    return ray;
}

vec3 Trace(Ray ray, Sphere spheres[MAX_SPHERES], inout uint state) {
    vec3 incomingLight = vec3(0.0);
    vec3 rayColor = vec3(1.0);

    for(int depth = 0; depth < maxDepth; depth++) {
        HitInfo hit = RayCollision(ray, spheres);
        
        if(!hit.hit) {
            incomingLight += rayColor * GetEnvironmentLight(ray);
            break;
        }

        // Russian Roulette termination
        // more dark the ray is, more likely to terminate
        if(depth > 5) {
            float q = max(0.05, 1.0 - length(rayColor));
            if(randomValue(state) < q) break;
            rayColor /= 1.0 - q;
        }
        RayTracingMaterial mat = hit.material;

        if(mat.ir >= 1.0) {
            ray = Refract(ray, hit, state);
            rayColor *= mat.colour;
            continue;
        } 

        // Add emitted light at every bounce, scaled by accumulated color
        incomingLight += rayColor * mat.emissionColour * mat.emissionStrength;

        // Combined specular probability and smoothness
        bool isSpecularBounce = randomValue(state) < mat.specularProbability;
        float specularBlend = mat.smoothness * float(isSpecularBounce);
        
        //Calculate reflection directions
        vec3 diffuseDir = normalize(hit.normal + randomInUnitSphere(state));
        vec3 specularDir = reflect(ray.direction, hit.normal);
        
        //Blend directions based on material properties
        ray.direction = normalize(mix(diffuseDir, specularDir, specularBlend));
        
        //Update ray color with proper material response
        rayColor *= mix(mat.colour, mat.specularColour, float(isSpecularBounce));

        ray.origin = hit.hitPoint + hit.normal * 0.0001;  
    }
    return incomingLight;
}


void main() {
    ivec2 fragCoord = ivec2(gl_FragCoord.xy);
    vec2 uv = (gl_FragCoord.xy * 2.0 - resolution.xy) / resolution.y;
    
    // Initialize PCG state
    uint state = uint(randomSeed) + uint(time) * 1000u +
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
                sphereSpecularProbs[i],
                sphereIRs[i]
            )
        );
    }

    // Temporal accumulation
    vec3 color = vec3(0.0);
    
    // Multiple samples per frame
    for(int i = 0; i < samplesPerFrame; i++) {
        ray.direction = normalize(ray.direction + randomInUnitSphere(state) * 0.0001);
        color += Trace(ray, spheres, state);
    }
    color /= float(samplesPerFrame);

    // Gamma correction
    color = pow(color, vec3(1.0/2.2));
    
    // Blend with accumulated result
    vec3 accumulated = texelFetch(accumulatedTex, fragCoord, 0).rgb;
    float a = 1.0 / (frameCount + 1.0 );
    FragColor = vec4(mix(accumulated, color, a), 1.0);
}