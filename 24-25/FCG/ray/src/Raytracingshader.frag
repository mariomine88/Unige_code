uniform float time;
uniform vec2 resolution;
uniform vec3 sphereCenter;
uniform float sphereRadius;


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


struct Sphere {
    vec3 center;
    float radius;
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
    
    // Create sphere using the uniform values
    Sphere sphere;
    sphere.center = sphereCenter;
    sphere.radius = sphereRadius;
    
    // Ray-sphere intersection test
    Ray ray = Ray(RO, RD);
    float t = intersectSphere(ray, sphere);
    
    vec3 finalColor;
    if (t > 0.0) {
        // Sphere hit - calculate normal and basic shading
        vec3 hitPoint = ray.at(t);
        vec3 normal = normalize(hitPoint - sphere.center);
        finalColor = normal * 0.5 + 0.5; // Normal visualization
        vec3 lightDir = vec3(1.0, 0.0, 0.0);  // Light direction
        float diff = max(dot(normal, lightDir), 0.0);
        //finalColor = vec3(1.0, 0.2, 0.2) * (diff * 0.8 + 0.2); // Red sphere with diffuse shading
    } else {
        // Background - sky gradient
        float t = (uv.y + 1.0) * 0.5;
        finalColor = mix(vec3(1.0, 1.0, 1.0), vec3(0.5, 0.7, 1.0), t);
    }
    
    gl_FragColor = vec4(finalColor, 1.0);
}