HitInfo trace(Ray ray) {
    HitInfo hit;
    hit.hit = false;
    hit.dst = 1e30;
    
    for(int i=0; i<MAX_SPHERES; i++) {
        float t = intersect(ray, spheres[i]);
        if(t > 0.001 && t < hit.dst) {
            hit.hit = true;
            hit.dst = t;
            hit.point = ray.origin + t * ray.direction;
            hit.normal = normalize(hit.point - spheres[i].center);
            hit.inside = dot(ray.direction, hit.normal) > 0.0;
            hit.mat = spheres[i].mat;
        }
    }
    return hit;
}

vec3 sky(Ray ray) {
    vec3 skyColorHorizon = vec3(0.788,0.859,0.992); 
    vec3 skyColorZenith = vec3(0.376,0.620,0.984);
    float skyGradientT = pow(smoothstep(0.0, 0.4, ray.direction.y), 0.35);
    
    return mix(skyColorHorizon, skyColorZenith, skyGradientT);
}

Ray Refract(Ray ray, HitInfo hit, inout uint state) {
    Material mat = hit.mat;
    float eta = mat.ir;
    vec3 normal = hit.normal;

    // Determine if the ray is inside the material
    if (hit.inside) {
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
    float random = rand(state); // Assume this generates a random value between 0 and 1

    // Check for total internal reflection or use Schlick's reflectance
    if (refracted == vec3(0.0) || random < reflectance) {
        ray.direction = reflect(ray.direction, normal);
    } else {
        ray.direction = refracted;
        normal = -normal; // Flip normal for refraction
    }

    ray.origin = hit.point + normal * 0.0001;
    return ray;
}

vec3 tracePath(Ray ray, inout uint state) {
    vec3 rayColor = vec3(1.0);
    vec3 incomingLight = vec3(0.0);
    
    for(int depth=0; depth<MAX_DEPTH; depth++) {
        HitInfo hit = trace(ray);
        if(!hit.hit) {
            incomingLight += rayColor * sky(ray);
            break;
        }
        
        // Russian Roulette termination (after a few bounces)
        if(depth > 3) {
            float p = max(rayColor.x, max(rayColor.y, rayColor.z));
            if(rand(state) >= p) break;
            // Add the energy we 'lose' by randomly terminating paths
            rayColor *= 1.0 / p;
        }
        
         if(hit.mat.ir >= 1.0) {
            ray = Refract(ray, hit, state);
            if(hit.inside){
                rayColor *= exp(-hit.mat.refractionColor * hit.dst);}
            else{
                rayColor *= hit.mat.colour;
            }
            continue;
        } 
        
        // Calculate reflection directions
        vec3 diffuseDir = normalize(hit.normal + randomUnitVector(state));
        vec3 specularDir = reflect(ray.direction, hit.normal);
        
        // Determine if this bounce is specular based on material properties
        bool isSpecularBounce = hit.mat.specularProb >= rand(state);
        
        // Mix between diffuse and specular based on material smoothness
        ray.direction = normalize(mix(diffuseDir, specularDir, hit.mat.smoothness * float(isSpecularBounce)));
        ray.origin = hit.point + hit.normal * 0.001;
        
        // Update ray color with material response
        rayColor *= hit.mat.colour;
        
        // Add emitted light at every bounce, scaled by accumulated color
        incomingLight += rayColor * hit.mat.emission * hit.mat.emissionStrength;
    }
    
    return incomingLight;
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    initSpheres();
    
    vec2 uv = (fragCoord.xy * 2.0 - iResolution.xy) / iResolution.y;

    // Calculate camera basis vectors
    float focal_length = length(lookfrom - lookat);
    vec3 w = normalize(lookfrom - lookat);  // Camera forward vector (points backwards)
    vec3 u = normalize(cross(vec3(0,1,0), w));      // Camera right vector
    vec3 v = cross(w, u);                   // Camera up vector (true up)
    
    // FOV calculations
    float theta = radians(cameraFov);
    float h = tan(theta / 2.0);
    float viewport_height = 2.0 * h;
    
    
    // Scale UV coordinates based on FOV
    uv *= viewport_height / 2.0;
    vec3 direction = normalize(vec3(-w + u * uv.x + v * uv.y));
    
    uint state = uint(iTime) * 563u + uint(iFrame)*26699u + uint(fragCoord.x)*456u + uint(fragCoord.y)*789u;
    
     // Temporal accumulation
    vec3 color = vec3(0.0);
    
    for (int index = 0; index < SAMPLES_PER_FRAME; ++index){
        vec3 offset = 0.01 * cross(direction , randomUnitVector(state));
        Ray ray = Ray(lookfrom + offset, direction);
    	color += tracePath(ray, state) / float(SAMPLES_PER_FRAME);
    }
    
    // Gamma correction
    color = pow(color, vec3(1.0/2.2));
    
    // average the frames together
    vec3 lastFrameColor = texture(iChannel0, fragCoord / iResolution.xy).rgb;
    color = mix(lastFrameColor, color, 1.0f / float(iFrame+1));

    // show the result
    fragColor = vec4(color, 1.0f);
}