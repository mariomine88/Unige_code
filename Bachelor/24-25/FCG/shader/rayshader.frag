precision mediump float;

uniform float u_time ;
uniform vec2 u_resolution ;

float sdSphere(vec3 p, float r) {
    return length(p) - r;
}

float sdBox(vec3 p, vec3 b) {
    vec3 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(d.x, max(d.y, d.z)), 0.0);
}

float smoothMin(float a, float b, float k) {
    float h = clamp(0.5 + 0.5 * (b - a) / k, 0.0, 1.0);
    return mix(b, a, h) - k * h * (1.0 - h);
}

float map(vec3 p) {
    vec3 sferepos = vec3(sin(u_time)*3.0, 0.0, 0.0); // sphere position

    float Sphere = sdSphere(p - sferepos, 1.0); // sphere
    float Box = sdBox(p, vec3(1.0)); // box

    float ground = p.y +1.0; // ground

    return min(ground, smoothMin(Sphere, Box, 2.0));
}


void main() {
    vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / u_resolution.y;

    vec3 ro = vec3(0.0, 0.0, -3.0);         // ray origin
    vec3 rd = normalize(vec3(uv, 1.0));     // ray direction
    vec3 col = vec3(0.0);                   // color accumulator

    float t = 0.;

    for (int i = 0; i < 80; i++) {
        vec3 p = ro + rd * t;           // ray position
        float d = map(p);               // distance to the scene
        t += d;

        if (d < 0.01 || t > 100.) {    // stop if we're close enough or too far
            break;
        }
    }

    col = vec3(t *.2);

    gl_FragColor = vec4(col, 1.0);
}