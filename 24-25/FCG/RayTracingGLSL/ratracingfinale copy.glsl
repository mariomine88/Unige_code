#version 300 es

/*
{
  "textures": [
    {
      "name": "u_texture",
      "path": "https://eoimages.gsfc.nasa.gov/images/imagerecords/73000/73909/world.topo.bathy.200412.3x5400x2700.jpg"
    }
  ]
}
*/

precision highp float;
uniform sampler2D previousFrame; // Previous accumulated frame
uniform int frameCount;          // Current frame count (0 for first frame)
out vec4 fragColor;
uniform vec2 u_resolution;
uniform float u_time;

uniform sampler2D u_texture; // Texture for the scene

bool environmentEnabled = true;
vec3 skyColorHorizon = vec3(0.7, 0.8, 1.0); 
vec3 skyColorZenith = vec3(0.3, 0.5, 0.8);
vec3 groundColor = vec3(0.4, 0.3, 0.2);
vec3 sundir = vec3(1.0, 0.7, 0.7);
float sunFocus = 128.0;
float sunIntensity = 1.0;

const int numSpheres = 1;
const int numTriangles = 1; 

//camera settings
float cameraFov = 90.0; // Field of view in degrees
vec3 lookfrom = vec3(0, 1, 5);   // Point camera is looking from
vec3 lookat = vec3(0, 1 , 0);  // Point camera is looking at
vec3 vup = vec3(0,1,0);     // Camera-relative "up" direction


int maxDepth = 30;
int samplesPerFrame = 50;


struct Ray {
    vec3 ori; // punto di origine del raggio
    vec3 dir; // versore (vettore a norma 1)
};


// struttura per i materiali
struct Material {
    vec3 colour;
    vec3 emissionColour;
    float emissionStrength;
    float smoothness;
    float specularProbability;
    float ir;
    bool useTexture; 
};

struct Sphere {
    vec3 center;
    float radius;
    Material material;
};

struct triangale {
    vec3 v0;
    vec3 v1;
    vec3 v2;
    Material material;
};


struct HitInfo {
    bool hit;
    float dst;
    vec3 hitPoint;
    vec3 normal;
    bool inside;
    Material material;
    vec2 uv;
};



Sphere spheres[numSpheres] = Sphere[](
    // No spheres in this example
    Sphere(vec3(0.0, 0.0, 0.0), 2.0, Material(vec3(0.8, 0.2, 0.2), vec3(0.87f, 0.11f, 0.11f), 1.0, 0.5, 0.5, 0.0,true))
    
);

triangale triangles[numTriangles] = triangale[](
    triangale(vec3(10.0, 10.0, 10.0),vec3(11.0, 11.0, 11.0), vec3(11.0, 11.0, 11.0), Material(vec3(0.8, 0.2, 0.2), vec3(0.87f, 0.11f, 0.11f), 1.0, 0.5, 0.5, 0.0 ,false))
);


vec2 getSphereUV(vec3 point, vec3 center) {
    vec3 dir = normalize(point - center);
    float u = 0.5 + atan(dir.z, dir.x) / (2.0 * 3.14159);
    float v = 0.5 - asin(dir.y) / 3.14159;
    return vec2(u, v);
}

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
float randomValueNormalDistribution(inout uint state){
    float theta = 2.0 * 3.1415926 * randomValue(state);
	float rho = sqrt(-2.0 * log(randomValue(state)));
	return rho * cos(theta);
}

vec3 randomUnitVector(inout uint state) {
    return normalize(vec3(randomValueNormalDistribution(state), randomValueNormalDistribution(state), randomValueNormalDistribution(state)));
} 

float intersectSphere(Ray ray, Sphere sphere) {
    vec3 oc = ray.ori - sphere.center;
    float a = dot(ray.dir, ray.dir);
    float b = 2.0 * dot(oc, ray.dir);
    float c = dot(oc, oc) - sphere.radius * sphere.radius;
    float discriminant = b * b - 4.0 * a * c;
    
    if(discriminant < 0.0) return -1.0;
    return (-b - sqrt(discriminant)) / (2.0 * a);
}

float intersectTriangle(Ray ray, triangale triangle) {
    vec3 v0 = triangle.v0;
    vec3 v1 = triangle.v1;
    vec3 v2 = triangle.v2;
    // Moller-Trumbore intersection algorithm
    vec3 edge1 = v1 - v0;
    vec3 edge2 = v2 - v0;
    vec3 h = cross(ray.dir, edge2);
    float a = dot(edge1, h);
    
    // If a is near zero, ray is parallel to triangle
    if (abs(a) < 1e-8) return -1.0; // Ray is parallel to triangle
    
    float f = 1.0 / a;
    vec3 s = ray.ori - v0;
    float u = f * dot(s, h);
    
    if (u < 0.0 || u > 1.0) return -1.0; // Outside triangle
    
    vec3 q = cross(s, edge1);
    float v = f * dot(ray.dir, q);
    
    if (v < 0.0 || u + v > 1.0) return -1.0; // Outside triangle
    
    float t = f * dot(edge2, q);
    
    if (t > 1e-8) return t; // Intersection
    else return -1.0; // No intersection
}

HitInfo RayCollision(Ray ray, Sphere spheres[numSpheres]) {
    HitInfo hit;
    hit.hit = false;
    hit.dst = 1e30;

    for(int i = 0; i < numSpheres; i++) {
        float t = intersectSphere(ray, spheres[i]);
        if(t > 0.00001 && t < hit.dst) {
            hit.hit = true;
            hit.dst = t;
            hit.hitPoint = ray.ori + t * ray.dir;
            hit.normal = normalize(hit.hitPoint - spheres[i].center);
            hit.inside = dot(ray.dir, hit.normal) < 0.0;
            hit.material = spheres[i].material;
            hit.uv = getSphereUV(hit.hitPoint, spheres[i].center);
       
        }
    }
    // Check for triangle intersections
    for(int i = 0; i < numTriangles; i++) {
        float t = intersectTriangle(ray, triangles[i]);
        if(t > 0.00001 && t < hit.dst) {
            hit.hit = true;
            hit.dst = t;
            hit.hitPoint = ray.ori + t * ray.dir;
            vec3 v0 = triangles[i].v0;
            vec3 v1 = triangles[i].v1;
            vec3 v2 = triangles[i].v2;
            vec3 edge1 = v1 - v0;
            vec3 edge2 = v2 - v0;
            hit.normal = normalize(cross(edge1, edge2));
            hit.inside = dot(ray.dir, hit.normal) < 0.0;
            hit.material = triangles[i].material;
        }
    }
    return hit;
}


vec3 GetEnvironmentLight(Ray ray) {
    if(!environmentEnabled) return vec3(0.0);
    
    float skyGradientT = pow(smoothstep(0.0, 0.4, ray.dir.y), 0.35);
    float groundToSkyT = smoothstep(-0.01, 0.0, ray.dir.y);
    vec3 skyGradient = mix(skyColorHorizon, skyColorZenith, skyGradientT);
    float sun = pow(max(0.0, dot(ray.dir, normalize(sundir))), sunFocus) * sunIntensity;
    
    return mix(groundColor, skyGradient, groundToSkyT) + sun * float(groundToSkyT >= 1.0);
}

Ray Refract(Ray ray, HitInfo hit, inout uint state) {
    Material mat = hit.material;
    float eta = mat.ir;
    vec3 normal = hit.normal;

    // Determine if the ray is inside the material
    if (hit.inside) {
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

    ray.ori = hit.hitPoint + normal * 0.0001;
    return ray;
}


vec3 Trace(Ray ray, inout uint state) {
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
        if(depth > 3) {
            float p = max(incomingLight.x, max(incomingLight.y, incomingLight.z));
            if (randomValue(state) >= p) break;
            // Add the energy we 'lose' by randomly terminating paths
            incomingLight *= 1.0f / p;
        }
        Material mat = hit.material;

        // Handle refractive materials (glass, water, etc.)
        if(mat.ir >= 1.0) {
            ray = Refract(ray, hit, state);
            rayColor *= mat.colour;
            continue;
        } 

        if(mat.useTexture) {
            rayColor *= texture(u_texture, hit.uv).rgb;
        } else {
            rayColor *= mat.colour;
        }

        //Calculate reflection directions
        vec3 diffuseDir = normalize(hit.normal + randomUnitVector(state));
        vec3 specularDir = reflect(ray.dir, hit.normal);

        bool isSpecularBounce = mat.specularProbability >= randomValue(state);
        ray.dir = normalize(mix(diffuseDir, specularDir, mat.smoothness * float(isSpecularBounce)));
        ray.ori = hit.hitPoint + hit.normal * 0.0001;  

        //Update ray color with proper material response
        rayColor *= mat.colour;

        // Add emitted light at every bounce, scaled by accumulated color
        incomingLight += rayColor * mat.emissionColour * mat.emissionStrength;
    }
    return incomingLight;
}


void main()
{
    if (gl_FragCoord.x < 200.0 && gl_FragCoord.y < 200.0) {
    vec2 debugUV = gl_FragCoord.xy / 200.0;
    fragColor = texture(u_texture, debugUV);
    return;
    }

    vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / u_resolution.y;
    // Calculate camera basis vectors
    float focal_length = length(lookfrom - lookat);
    vec3 w = normalize(lookfrom - lookat);  // Camera forward vector (points backwards)
    vec3 u = normalize(cross(vup, w));      // Camera right vector
    vec3 v = cross(w, u);                   // Camera up vector (true up)

    // FOV calculations
    float theta = radians(cameraFov);
    float h = tan(theta / 2.0);
    float viewport_height = 2.0 * h;

    // Scale UV coordinates based on FOV
    uv *= viewport_height / 2.0;

    vec3 direction = normalize(vec3(-w + u * uv.x + v * uv.y));

    // Initialize PCG state
    uint state = uint(u_time) * 1000u +
                uint(gl_FragCoord.x) * 1973u + 
                uint(gl_FragCoord.y) * 9277u ;

    vec3 color = vec3(0.0);
    // Perform multiple samples per pixel for anti-aliasing and soft shadows
    for (int index = 0; index < samplesPerFrame; ++index) {
        // Apply a small random offset to the ray for anti-aliasing
        vec3 offset = 0.01 * cross(direction, randomUnitVector(state));
        
        // Create a ray from camera position with slightly offset direction
        Ray ray = Ray(lookfrom + offset, direction);
        
        // Accumulate path traced color and average across samples
        color += Trace(ray, state) / float(samplesPerFrame);
    }

    // Apply gamma correction
    color = pow(color, vec3(1.0/2.0)); // Gamma 2.0

    if (frameCount > 0) {
        // Get the previous accumulated result
        vec2 texCoord = gl_FragCoord.xy / u_resolution.xy;
        vec3 previousColor = texture(previousFrame, texCoord).rgb;
        
        // Blend with current frame using progressive weight
        float blendWeight = 1.0 / float(frameCount + 1);
        color = mix(previousColor, color, blendWeight);
        // Alternative formula: color = previousColor * (1.0 - blendWeight) + color * blendWeight;
    }

    fragColor = vec4(color, 1.0f);
}