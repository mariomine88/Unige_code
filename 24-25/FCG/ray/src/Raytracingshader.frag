uniform float time;
uniform vec2 resolution;
uniform int numSpheres;

uniform sampler2D accumulatedTex;
uniform float frameCount;

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
#define maxDepth 10


float rand(vec2 co) {
    return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
}

// Simpler version for random hemisphere direction
vec3 randomHemisphereDirection(vec3 normal, vec2 seed) {
    // Create a random direction
    vec3 randVec = vec3(
        rand(seed) * 2.0 - 1.0,
        rand(seed + vec2(1.0, 2.0)) * 2.0 - 1.0,
        rand(seed + vec2(3.0, 4.0)) * 2.0 - 1.0
    );
    
    // Normalize and ensure it's in the correct hemisphere
    randVec = normalize(randVec);
    if (dot(randVec, normal) < 0.0) {
        randVec = -randVec;
    }
    
    return normalize(randVec);
}

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
    vec3 oc = ray.origin - sphere.center;
    float a = dot(ray.direction, ray.direction);
    float b = 2.0 * dot(oc, ray.direction);
    float c = dot(oc, oc) - sphere.radius * sphere.radius;
    float discriminant = b*b - 4.0*a*c;
    
    if (discriminant < 0.0) {
        return -1.0;
    } else {
        return (-b - sqrt(discriminant)) / (2.0*a);
    }
}



void main() {
    vec2 uv = (gl_FragCoord.xy * 2.0 - resolution.xy) / resolution.y;

    vec3 RO = vec3(0.0, 0.0, 0.0); // Ray Origin
    vec3 RD = normalize(vec3(uv, -1.0)); // Ray Direction
    Ray ray = Ray(RO, RD);
    
    vec3 color = vec3(0.0);
    vec3 throughput = vec3(1.0);

    for (int depth = 0; depth < maxDepth; depth++) {
        float closestT = 1e30; // Very large number
        int hitIndex = -1;
        // Find closest sphere intersection
        for (int i = 0; i < numSpheres; i++) {
            float t = intersectSphere(ray, Sphere(sphereCenters[i], sphereRadii[i] , RayTracingMaterial(sphereColors[i], sphereEmissionColors[i], sphereSpecularColors[i], sphereEmissionStrengths[i], sphereSmoothness[i], sphereSpecularProbs[i])));
            if (t > 0.0 && t < closestT) {
                closestT = t;
                hitIndex = i;
            }
        }
        
        if (hitIndex == -1) {
            // Apply background color with accumulated throughput
            float t = (uv.y + 1.0) * 0.5;
            vec3 HitColor = mix(vec3(1.0, 1.0, 1.0), vec3(0.5, 0.7, 1.0), t);
            color += throughput*1.1 * HitColor;
            break;
        }
        
        // Calculate surface interaction
        vec3 hitPoint = ray.at(closestT);
        vec3 normal = normalize(hitPoint - sphereCenters[hitIndex]);
        
        // Update color throughput
        throughput *= 0.4 * sphereColors[hitIndex];
        

        // Generate new ray direction with surface offset
        vec3 newDir;
        if (sphereSmoothness[hitIndex] == 1.0) {
            // Diffuse reflection
            newDir = ray.direction - 2.0 * dot(ray.direction, normal) * normal;
        } else {
            vec2 seed = uv * (float(depth) + time);
            newDir = randomHemisphereDirection(normal, seed);
        }
        ray = Ray(hitPoint + normal * 0.0001, newDir);
    }

    vec2 texCoord = gl_FragCoord.xy / resolution;
    vec3 accumulatedColor = texture2D(accumulatedTex, texCoord).rgb;
    float samples = frameCount + 1.0;
    color = pow(color, vec3(1.0/2.));
    vec3 finalColor = (accumulatedColor * frameCount + color) / samples;
    gl_FragColor = vec4(finalColor, 1.0);
}