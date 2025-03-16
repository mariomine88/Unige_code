uniform float time;
uniform vec2 resolution;
uniform int numSpheres;

// Define maximum number of spheres (must match C++ code)
#define MAX_SPHERES 30
uniform vec3 sphereCenters[MAX_SPHERES];
uniform float sphereRadii[MAX_SPHERES];

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

struct RayTracingMaterial{
	vec3 colour;
	vec3 emissionColour;
	vec3 specularColour;
	float emissionStrength;
	float smoothness;
	float specularProbability;
};

struct Sphere{
    vec3 position;
	float radius;
	RayTracingMaterial material;
};

// Ray-sphere intersection function
//quewsta funzione calcola l'intersezione tra un raggio e una sfera 
//cioè calcola la distanza tra il punto di origine del raggio e il punto di intersezione con la sfera
float intersectSphere(Ray ray, Sphere sphere) {
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
    
    // Create ray
    Ray ray = Ray(RO, RD);
    
    // Variables to track closest intersection
    float closestT = 1e30; // Very large number
    int hitSphereIndex = -1;
    
    // Check intersection with all spheres
    for (int i = 0; i < numSpheres; i++) {
        Sphere sphere;
        sphere.center = sphereCenters[i];
        sphere.radius = sphereRadii[i];
        
        float t = intersectSphere(ray, sphere);
        if (t > 0.0 && t < closestT) {
            closestT = t;
            hitSphereIndex = i;
        }
    }
    
    vec3 finalColor;
    if (hitSphereIndex >= 0) {
        // We hit a sphere
        vec3 hitPoint = ray.at(closestT);
        vec3 sphereCenter = sphereCenters[hitSphereIndex];
        vec3 normal = normalize(hitPoint - sphereCenter);
        
        // Different coloring based on which sphere was hit
        if (hitSphereIndex == 0) {
            // First sphere - red with normal shading
            vec3 baseColor = vec3(1.0, 0.2, 0.2); 
            finalColor = baseColor * (normal * 0.5 + 0.5);
        } else if (hitSphereIndex == 1) {
            // Second sphere - blue with normal shading
            vec3 baseColor = vec3(0.2, 0.4, 1.0);
            finalColor = baseColor * (normal * 0.5 + 0.5);
        } else {
            // Any other spheres - normal visualization
            finalColor = normal * 0.5 + 0.5;
        }
        
        // Add basic lighting
        vec3 lightDir = normalize(vec3(1.0, 1.0, 1.0));
        float diff = max(dot(normal, lightDir), 0.0);
        finalColor = finalColor * (diff * 0.6 + 0.4); // Diffuse + ambient
    } else {
        // Background - sky gradient
        float t = (uv.y + 1.0) * 0.5;
        finalColor = mix(vec3(1.0, 1.0, 1.0), vec3(0.5, 0.7, 1.0), t);
    }
    
    gl_FragColor = vec4(finalColor, 1.0);
}