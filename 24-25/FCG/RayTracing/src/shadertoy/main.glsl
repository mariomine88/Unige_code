struct Ray {
    vec3 ori;
    vec3 dir;
};

struct HitInfo {
    bool hit;
    float dst;
    vec3 point;
    vec3 normal;
    bool inside;
    Material material;
};

// PCG Random Number Generator
uint pcg_hash(inout uint state) {
    state = state * 747796405u + 2891336453u;
    uint word = ((state >> ((state >> 28u) + 4u)) ^ state) * 277803737u;
    return (word >> 22u) ^ word;
}

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

float intersectSphere(Ray ray, Sphere s) {
    vec3 oc = ray.ori - s.center;
    float a = dot(ray.dir, ray.dir);
    float b = 2.0 * dot(oc, ray.dir);
    float c = dot(oc, oc) - s.radius * s.radius;
    float discriminant = b * b - 4.0 * a * c;
    if(discriminant < 0.0) return -1.0;
    
    return (-b - sqrt(discriminant)) / (2.0 * a);
}


HitInfo RayCollision(Ray ray) {
    HitInfo hit;
    hit.hit = false;
    hit.dst = 1e30;
    
    for(int i=0; i<MAX_SPHERES; i++) {
        float t = intersectSphere(ray, spheres[i]);
        if(t > 0.0001 && t < hit.dst) {
            hit.hit = true;
            hit.dst = t;
            hit.point = ray.ori + t * ray.dir;
            hit.normal = normalize(hit.point - spheres[i].center);
            hit.inside = dot(ray.dir, hit.normal) < 0.0;
            hit.material = spheres[i].material;
        }
    }
    return hit;
}

vec3 GetEnvironmentLight(Ray ray) {
    if (!environmentLight) return vec3(0);
    vec3 skyColorHorizon = vec3(0.7, 0.8, 1.0); 
    vec3 skyColorZenith = vec3(0.3, 0.5, 0.8);
    vec3 groundColor = vec3(0.4, 0.3, 0.2);
    vec3 sunDirection = vec3(0.0, 0.7, -0.7);
    float sunFocus = 128.0;
    float sunIntensity = 5.0;

    // Calculate sky gradient based on ray direction
    // Smoothstep for sky gradient transition
    float skyGradientT = pow(smoothstep(0.0, 0.4, ray.dir.y), 0.35);
    float groundToSkyT = smoothstep(-0.01, 0.0, ray.dir.y);
    vec3 skyGradient = mix(skyColorHorizon, skyColorZenith, skyGradientT);
    float sun = pow(max(0.0, dot(ray.dir, normalize(sunDirection))), sunFocus) * sunIntensity;
    
    return mix(groundColor, skyGradient, groundToSkyT) + sun * float(groundToSkyT >= 1.0);
}

Ray Refract(Ray ray, HitInfo hit, inout uint state) {
    Material mat = hit.material;
    float eta = mat.ir;
    vec3 normal = hit.normal;

    // Determine if the ray is inside the material
    if (!hit.inside) {
        normal = -normal; // Flip normal to face incoming ray
    } else {
        eta = 1.0 / eta; // Adjust eta for entering the material
    }

    // Calculate the refracted direction
    vec3 refracted = refract(ray.dir, normal, eta);

    // Compute cosine of the incidence angle (adjusted for hemisphere)
    float cos_theta = min(abs(dot(normalize(ray.dir), normal)), 1.0);
    // Schlick's approximation for Fresnel reflectance
    float R0 = pow((1.0 - eta) / (1.0 + eta), 2.0);
    float reflectance = R0 + (1.0 - R0) * pow(1.0 - cos_theta, 5.0);

    // Use a random value to decide between reflection and refraction
    float random = randomValue(state); // Assume this generates a random value between 0 and 1

    // Check for total internal reflection or use Schlick's reflectance
    if (refracted == vec3(0.0) || random < reflectance) {
        vec3 specularDir = reflect(ray.dir, normal);
        vec3 diffuseDir = normalize(hit.normal + randomUnitVector(state));
        ray.dir = normalize(mix(diffuseDir, specularDir, mat.smoothness));    
    } else {
        ray.dir = refracted;
        normal = -normal; // Flip normal for refraction
    }

    ray.ori = hit.point + normal * 0.0001;
    return ray;
}

vec3 Trace(Ray ray, inout uint state) {
    vec3 rayColor = vec3(1.0);
    vec3 incomingLight = vec3(0.0);
    
    for(int depth=0; depth<MAX_DEPTH; depth++) {
        HitInfo hit = RayCollision(ray);
        if(!hit.hit) {
            incomingLight += rayColor * GetEnvironmentLight(ray);
            break;
        }
        
        // Russian Roulette termination (after a few bounces)
        if(depth > 3) {
            float p = max(rayColor.x, max(rayColor.y, rayColor.z));
            if(randomValue(state) >= p) break;
            // Add the energy we 'lose' by randomly terminating paths
            rayColor *= 1.0 / p;
        }

        Material mat = hit.material;
        
        // Handle refractive materials (glass, water, etc.)
        if(mat.ir >= 1.0) {
            ray = Refract(ray, hit, state);
            if (hit.inside) {
                // If inside a transparent material, apply absorption color
                // Apply absorption color for transparent materials
                rayColor *= exp(-mat.absorptionColour * hit.dst);
            } else {
                // If outside, apply the material color
                rayColor *= mat.colour;
            }
            continue;
        } 
        
        // Calculate reflection directions
        vec3 diffuseDir = normalize(hit.normal + randomUnitVector(state));
        vec3 specularDir = reflect(ray.dir, hit.normal);
        
        // Determine if this bounce is specular based on material properties
        bool isSpecularBounce = mat.specularProbability >= randomValue(state);
        
        // Mix between diffuse and specular based on material smoothness
        ray.dir = normalize(mix(diffuseDir, specularDir, mat.smoothness * float(isSpecularBounce)));
        rayColor *= (isSpecularBounce) ? mat.colour : vec3(1.0);
        ray.ori = hit.point + hit.normal * 0.001;
        
        // Update ray color with material response
        rayColor *= mat.colour;
        
        // Add emitted light at every bounce, scaled by accumulated color
        incomingLight += rayColor * mat.emissionColour * mat.emissionStrength;
    }
    
    return incomingLight;
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    // Initialize the scene with spheres and materials
    initSpheres();
    
    // Convert from pixel coordinates to normalized device coordinates (NDC)
    // Scale to make aspect ratio correct (divide by height to make y range [-1,1])
    vec2 uv = (fragCoord.xy * 2.0 - iResolution.xy) / iResolution.y;

    // ----- Camera Setup -----
    // Create an orthonormal basis for the camera
    vec3 w = normalize(lookfrom - lookat);  // Forward vector (towards camera)
    vec3 u = normalize(cross(vec3(0,1,0), w));  // Right vector
    vec3 v = cross(w, u);                       // Up vector
    
    // Calculate viewport dimensions from field of view
    float theta = radians(cameraFov);  // Convert FOV from degrees to radians
    float h = tan(theta / 2.0);        // Half-height of viewport at focal distance
    float viewport_height = 2.0 * h;   // Full viewport height
    
    // Scale UV coordinates to match viewport dimensions
    uv *= viewport_height / 2.0;
    
    // Calculate ray direction through the current pixel
    vec3 direction = normalize(vec3(-w + u * uv.x + v * uv.y));
    
    // ----- Random State Initialization -----
    // Create unique random seed for each pixel and frame
    uint state = uint(iTime) * 563u + uint(iFrame)*26699u + uint(fragCoord.x)*456u + uint(fragCoord.y)*789u;
    
    // ----- Sampling & Integration -----
    vec3 color = vec3(0.0);
    
    // Perform multiple samples per pixel for anti-aliasing and soft shadows
    for (int index = 0; index < SAMPLES_PER_FRAME; ++index) {
        // Apply a small random offset to the ray for anti-aliasing
        vec3 offset = 0.005 * cross(direction, randomUnitVector(state));
        
        // Create a ray from camera position with slightly offset direction
        Ray ray = Ray(lookfrom + offset, direction);
        
        // Accumulate path traced color and average across samples
        color += Trace(ray, state) / float(SAMPLES_PER_FRAME);
    }
    
    // Apply gamma correction (convert from linear to sRGB color space)
    color = pow(color, vec3(1.0/2.2));
    
    // ----- Temporal Accumulation (Frame Blending) -----
    // Retrieve previous frame's color for the same pixel
    vec3 lastFrameColor = texture(iChannel0, fragCoord / iResolution.xy).rgb;
    
    // Blend current frame with previous frames (progressive rendering)
    // Weight decreases as frame count increases for stable convergence
    color = mix(lastFrameColor, color, 1.0f / float(iFrame+1));

    // Output the final color
    fragColor = vec4(color, 1.0f);
}