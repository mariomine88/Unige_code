#version 300 es

precision highp float;
uniform vec2 u_resolution;
out vec4 fragColor;

struct Ray {
    vec3 ori;
    vec3 dir; 
};

struct Material {
    vec3 colour;
};

struct Sphere {
    vec3 center;
    float radius;
    Material material;
};

struct HitInfo {
    bool hit;
    float dst;
    vec3 hitPoint;
    vec3 normal;
    Material material;
};

const int numSpheres = 1;
Sphere spheres[numSpheres] = Sphere[](
    Sphere(vec3(0.0, 1.0, 0.0), 1.0, Material(vec3(0.8, 0.2, 0.2)))
);

float intersectSphere(Ray ray, Sphere sphere) {
    vec3 oc = ray.ori - sphere.center;
    float a = dot(ray.dir, ray.dir);
    float b = 2.0 * dot(oc, ray.dir);
    float c = dot(oc, oc) - sphere.radius * sphere.radius;
    float discriminant = b * b - 4.0 * a * c;
    
    if(discriminant < 0.0) return -1.0;
    return (-b - sqrt(discriminant)) / (2.0 * a);
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
            hit.material = spheres[i].material;
        }
    }
    return hit;
}


vec3 GetEnvironmentLight(Ray ray) {
    vec3 skyColorHorizon = vec3(0.2, 0.5, 1.0);
    vec3 skyColorZenith = vec3(0.1, 0.2, 0.5);
    
    return mix(skyColorHorizon, skyColorZenith, ray.dir.y);
}

vec3 Trace(Ray ray) {
    vec3 incomingLight = vec3(0.0);

    HitInfo hit = RayCollision(ray, spheres);
    if (hit.hit){
        incomingLight = hit.material.colour;
    } else {
        incomingLight = GetEnvironmentLight(ray);
    }
    return incomingLight;
}


void main()
{
    vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / u_resolution.y;

    Ray ray;
    ray.ori = vec3(0.0, 0.0, 5.0); // Camera position
    ray.dir = normalize(vec3(uv, -1.0)); // Ray direction

    fragColor = vec4(Trace(ray),1.0f);
}
