#version 300 es
precision highp float;
precision highp sampler2D;
precision highp samplerCube;

uniform float time;
uniform vec2 resolution;
uniform sampler2D iChannel0; // Accumulation texture
uniform samplerCube iChannel1; // Environment map

out vec4 FragColor;

const float c_minimumRayHitTime = 0.01;
const float c_rayPosNormalNudge = 0.01;
const float c_superFar = 10000.0;
const float c_FOVDegrees = 90.0;
const int c_numBounces = 8;
const int c_numRendersPerFrame = 1;
const float c_pi = 3.14159265359;
const float c_twopi = 2.0 * c_pi;

struct SRayHitInfo {
    float dist;
    vec3 normal;
    vec3 albedo;
    vec3 emissive;
};

uint wang_hash(inout uint seed) {
    seed = uint(seed ^ uint(61)) ^ uint(seed >> uint(16));
    seed *= uint(9);
    seed = seed ^ (seed >> 4);
    seed *= uint(0x27d4eb2d);
    seed = seed ^ (seed >> 15);
    return seed;
}

float RandomFloat01(inout uint state) {
    return float(wang_hash(state)) / 4294967296.0;
}

vec3 RandomUnitVector(inout uint state) {
    float z = RandomFloat01(state) * 2.0 - 1.0;
    float a = RandomFloat01(state) * c_twopi;
    float r = sqrt(1.0 - z * z);
    float x = r * cos(a);
    float y = r * sin(a);
    return vec3(x, y, z);
}

float ScalarTriple(vec3 u, vec3 v, vec3 w) {
    return dot(cross(u, v), w);
}

bool TestQuadTrace(in vec3 rayPos, in vec3 rayDir, inout SRayHitInfo info, in vec3 a, in vec3 b, in vec3 c, in vec3 d) {
    // calculate normal and flip vertices order if needed
    vec3 normal = normalize(cross(c-a, c-b));
    if (dot(normal, rayDir) > 0.0f)
    {
        normal *= -1.0f;
        
		vec3 temp = d;
        d = a;
        a = temp;
        
        temp = b;
        b = c;
        c = temp;
    }
    
    vec3 p = rayPos;
    vec3 q = rayPos + rayDir;
    vec3 pq = q - p;
    vec3 pa = a - p;
    vec3 pb = b - p;
    vec3 pc = c - p;
    
    // determine which triangle to test against by testing against diagonal first
    vec3 m = cross(pc, pq);
    float v = dot(pa, m);
    vec3 intersectPos;
    if (v >= 0.0f)
    {
        // test against triangle a,b,c
        float u = -dot(pb, m);
        if (u < 0.0f) return false;
        float w = ScalarTriple(pq, pb, pa);
        if (w < 0.0f) return false;
        float denom = 1.0f / (u+v+w);
        u*=denom;
        v*=denom;
        w*=denom;
        intersectPos = u*a+v*b+w*c;
    }
    else
    {
        vec3 pd = d - p;
        float u = dot(pd, m);
        if (u < 0.0f) return false;
        float w = ScalarTriple(pq, pa, pd);
        if (w < 0.0f) return false;
        v = -v;
        float denom = 1.0f / (u+v+w);
        u*=denom;
        v*=denom;
        w*=denom;
        intersectPos = u*a+v*d+w*c;
    }
    
    float dist;
    if (abs(rayDir.x) > 0.1f)
    {
        dist = (intersectPos.x - rayPos.x) / rayDir.x;
    }
    else if (abs(rayDir.y) > 0.1f)
    {
        dist = (intersectPos.y - rayPos.y) / rayDir.y;
    }
    else
    {
        dist = (intersectPos.z - rayPos.z) / rayDir.z;
    }
    
	if (dist > c_minimumRayHitTime && dist < info.dist)
    {
        info.dist = dist;        
        info.normal = normal;        
        return true;
    }    
    
    return false;
}

bool TestSphereTrace(in vec3 rayPos, in vec3 rayDir, inout SRayHitInfo info, in vec4 sphere) 
{
	//get the vector from the center of this sphere to where the ray begins.
	vec3 m = rayPos - sphere.xyz;

    //get the dot product of the above vector and the ray's vector
	float b = dot(m, rayDir);

	float c = dot(m, m) - sphere.w * sphere.w;

	//exit if r's origin outside s (c > 0) and r pointing away from s (b > 0)
	if(c > 0.0 && b > 0.0)
		return false;

	//calculate discriminant
	float discr = b * b - c;

	//a negative discriminant corresponds to ray missing sphere
	if(discr < 0.0)
		return false;
    
	//ray now found to intersect sphere, compute smallest t value of intersection
    bool fromInside = false;
	float dist = -b - sqrt(discr);
    if (dist < 0.0f)
    {
        fromInside = true;
        dist = -b + sqrt(discr);
    }
    
	if (dist > c_minimumRayHitTime && dist < info.dist)
    {
        info.dist = dist;        
        info.normal = normalize((rayPos+rayDir*dist) - sphere.xyz) * (fromInside ? -1.0f : 1.0f);
        return true;
    }
    
    return false;
}

void TestSceneTrace(in vec3 rayPos, in vec3 rayDir, inout SRayHitInfo hitInfo) 
{    
    // to move the scene around, since we can't move the camera yet
    vec3 sceneTranslation = vec3(0.0f, 0.0f, 10.0f);
    vec4 sceneTranslation4 = vec4(sceneTranslation, 0.0f);
    
   	// back wall
    {
        vec3 A = vec3(-12.6f, -12.6f, 25.0f) + sceneTranslation;
        vec3 B = vec3( 12.6f, -12.6f, 25.0f) + sceneTranslation;
        vec3 C = vec3( 12.6f,  12.6f, 25.0f) + sceneTranslation;
        vec3 D = vec3(-12.6f,  12.6f, 25.0f) + sceneTranslation;
        if (TestQuadTrace(rayPos, rayDir, hitInfo, A, B, C, D))
        {
            hitInfo.albedo = vec3(0.7f, 0.7f, 0.7f);
            hitInfo.emissive = vec3(0.0f, 0.0f, 0.0f);
        }
	}    
    
    // floor
    {
        vec3 A = vec3(-12.6f, -12.45f, 25.0f) + sceneTranslation;
        vec3 B = vec3( 12.6f, -12.45f, 25.0f) + sceneTranslation;
        vec3 C = vec3( 12.6f, -12.45f, 15.0f) + sceneTranslation;
        vec3 D = vec3(-12.6f, -12.45f, 15.0f) + sceneTranslation;
        if (TestQuadTrace(rayPos, rayDir, hitInfo, A, B, C, D))
        {
            hitInfo.albedo = vec3(0.7f, 0.7f, 0.7f);
            hitInfo.emissive = vec3(0.0f, 0.0f, 0.0f);
        }        
    }
    
    // cieling
    {
        vec3 A = vec3(-12.6f, 12.5f, 25.0f) + sceneTranslation;
        vec3 B = vec3( 12.6f, 12.5f, 25.0f) + sceneTranslation;
        vec3 C = vec3( 12.6f, 12.5f, 15.0f) + sceneTranslation;
        vec3 D = vec3(-12.6f, 12.5f, 15.0f) + sceneTranslation;
        if (TestQuadTrace(rayPos, rayDir, hitInfo, A, B, C, D))
        {
            hitInfo.albedo = vec3(0.7f, 0.7f, 0.7f);
            hitInfo.emissive = vec3(0.0f, 0.0f, 0.0f);
        }        
    }    
    
    // left wall
    {
        vec3 A = vec3(-12.5f, -12.6f, 25.0f) + sceneTranslation;
        vec3 B = vec3(-12.5f, -12.6f, 15.0f) + sceneTranslation;
        vec3 C = vec3(-12.5f,  12.6f, 15.0f) + sceneTranslation;
        vec3 D = vec3(-12.5f,  12.6f, 25.0f) + sceneTranslation;
        if (TestQuadTrace(rayPos, rayDir, hitInfo, A, B, C, D))
        {
            hitInfo.albedo = vec3(0.7f, 0.1f, 0.1f);
            hitInfo.emissive = vec3(0.0f, 0.0f, 0.0f);
        }        
    }
    
    // right wall 
    {
        vec3 A = vec3( 12.5f, -12.6f, 25.0f) + sceneTranslation;
        vec3 B = vec3( 12.5f, -12.6f, 15.0f) + sceneTranslation;
        vec3 C = vec3( 12.5f,  12.6f, 15.0f) + sceneTranslation;
        vec3 D = vec3( 12.5f,  12.6f, 25.0f) + sceneTranslation;
        if (TestQuadTrace(rayPos, rayDir, hitInfo, A, B, C, D))
        {
            hitInfo.albedo = vec3(0.1f, 0.7f, 0.1f);
            hitInfo.emissive = vec3(0.0f, 0.0f, 0.0f);
        }        
    }    
    
    // light
    {
        vec3 A = vec3(-5.0f, 12.4f,  22.5f) + sceneTranslation;
        vec3 B = vec3( 5.0f, 12.4f,  22.5f) + sceneTranslation;
        vec3 C = vec3( 5.0f, 12.4f,  17.5f) + sceneTranslation;
        vec3 D = vec3(-5.0f, 12.4f,  17.5f) + sceneTranslation;
        if (TestQuadTrace(rayPos, rayDir, hitInfo, A, B, C, D))
        {
            hitInfo.albedo = vec3(0.0f, 0.0f, 0.0f);
            hitInfo.emissive = vec3(1.0f, 0.9f, 0.7f) * 20.0f;
        }        
    }
    
	if (TestSphereTrace(rayPos, rayDir, hitInfo, vec4(-9.0f, -9.5f, 20.0f, 3.0f)+sceneTranslation4))
    {
        hitInfo.albedo = vec3(0.9f, 0.9f, 0.75f);
        hitInfo.emissive = vec3(0.0f, 0.0f, 0.0f);        
    } 
    
	if (TestSphereTrace(rayPos, rayDir, hitInfo, vec4(0.0f, -9.5f, 20.0f, 3.0f)+sceneTranslation4))
    {
        hitInfo.albedo = vec3(0.9f, 0.75f, 0.9f);
        hitInfo.emissive = vec3(0.0f, 0.0f, 0.0f);        
    }    
    
	if (TestSphereTrace(rayPos, rayDir, hitInfo, vec4(9.0f, -9.5f, 20.0f, 3.0f)+sceneTranslation4))
    {
        hitInfo.albedo = vec3(0.75f, 0.9f, 0.9f);
        hitInfo.emissive = vec3(0.0f, 0.0f, 0.0f);
    }    
}

vec3 GetColorForRay(in vec3 startRayPos, in vec3 startRayDir, inout uint rngState) 
{
    // initialize
    vec3 ret = vec3(0.0f, 0.0f, 0.0f);
    vec3 throughput = vec3(1.0f, 1.0f, 1.0f);
    vec3 rayPos = startRayPos;
    vec3 rayDir = startRayDir;
    
    for (int bounceIndex = 0; bounceIndex <= c_numBounces; ++bounceIndex)
    {
        // shoot a ray out into the world
        SRayHitInfo hitInfo;
        hitInfo.dist = c_superFar;
        TestSceneTrace(rayPos, rayDir, hitInfo);
        
        // if the ray missed, we are done
        if (hitInfo.dist == c_superFar)
        {
            ret += texture(iChannel1, rayDir).rgb * throughput;
            break;
        }
        
		// update the ray position
        rayPos = (rayPos + rayDir * hitInfo.dist) + hitInfo.normal * c_rayPosNormalNudge;
        
        // calculate new ray direction, in a cosine weighted hemisphere oriented at normal
        rayDir = normalize(hitInfo.normal + RandomUnitVector(rngState));        
        
		// add in emissive lighting
        ret += hitInfo.emissive * throughput;
        
        // update the colorMultiplier
        throughput *= hitInfo.albedo;      
    }
 
    // return pixel color
    return ret;
}


void main() {
    uint rngState = uint(uint(gl_FragCoord.x) * 1973u + uint(gl_FragCoord.y) * 9277u + uint(iFrame) * 26699u) | 1u;
    
    vec3 rayPosition = vec3(0.0);
    float cameraDistance = 1.0 / tan(c_FOVDegrees * 0.5 * c_pi / 180.0);
    
    vec2 uv = (gl_FragCoord.xy / iResolution) * 2.0 - 1.0;
    vec3 rayTarget = vec3(uv, cameraDistance);
    rayTarget.y /= iResolution.x / iResolution.y;
    
    vec3 rayDir = normalize(rayTarget - rayPosition);
    
    vec3 color = vec3(0.0);
    for(int i = 0; i < c_numRendersPerFrame; i++) {
        color += GetColorForRay(rayPosition, rayDir, rngState) / float(c_numRendersPerFrame);
    }
    
    vec3 lastFrameColor = texture(iChannel0, gl_FragCoord.xy / iResolution).rgb;
    color = mix(lastFrameColor, color, 1.0 / float(iFrame + 1));
    
    FragColor = vec4(color, 1.0);
}