uniform vec2 resolution;
uniform float time;
uniform vec4 models[64];
uniform int numModels;

struct Material {
    vec3 albedo;
    float metallic;
    float roughness;
};

struct Ray {
    vec3 origin;
    vec3 direction;
};

struct Hit {
    float distance;
    vec3 position;
    vec3 normal;
    Material material;
};

// Ray-object intersection functions
Hit sceneIntersect(Ray ray) {
    Hit hit;
    hit.distance = -1.0;
    
    for (int i = 0; i < numModels; ++i) {
        vec4 posData = models[i * 3];
        vec4 matData1 = models[i * 3 + 1];
        vec4 matData2 = models[i * 3 + 2];
        
        Material mat;
        mat.albedo = matData1.rgb;
        mat.metallic = matData1.a;
        mat.roughness = matData2.r;
        
        // Sphere intersection example
        vec3 center = posData.xyz;
        float radius = 0.5;
        
        vec3 oc = ray.origin - center;
        float a = dot(ray.direction, ray.direction);
        float b = 2.0 * dot(oc, ray.direction);
        float c = dot(oc, oc) - radius*radius;
        float disc = b*b - 4.0*a*c;
        
        if (disc > 0.0) {
            float t = (-b - sqrt(disc)) / (2.0*a);
            if (t > 0.0 && (hit.distance < 0.0 || t < hit.distance)) {
                hit.distance = t;
                hit.position = ray.origin + t*ray.direction;
                hit.normal = normalize(hit.position - center);
                hit.material = mat;
            }
        }
    }
    
    return hit;
}

// Ray tracing main function
void main() {
    vec2 uv = (gl_FragCoord.xy / resolution) * 2.0 - 1.0;
    uv.x *= resolution.x / resolution.y;
    
    Ray ray;
    ray.origin = vec3(0, 0, 3);
    ray.direction = normalize(vec3(uv, -1.0));
    
    Hit hit = sceneIntersect(ray);
    
    vec3 color = vec3(0.1);
    if (hit.distance > 0.0) {
        // Basic lighting
        vec3 lightPos = vec3(2, 5, 3);
        vec3 lightDir = normalize(lightPos - hit.position);
        float diff = max(dot(hit.normal, lightDir), 0.0);
        vec3 diffuse = diff * hit.material.albedo;
        
        // Specular
        vec3 viewDir = normalize(ray.origin - hit.position);
        vec3 reflectDir = reflect(-lightDir, hit.normal);
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32.0);
        vec3 specular = spec * vec3(0.5) * hit.material.metallic;
        
        color = diffuse * (1.0 - hit.material.metallic) + specular;
    }
    
    gl_FragColor = vec4(color, 1.0);
}