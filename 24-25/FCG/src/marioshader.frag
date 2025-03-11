uniform float time;
uniform vec2 resolution;

vec3 palette(float t) {
    vec3 a = vec3(0.5, 0.5, 0.5);
    vec3 b = vec3(0.5, 0.5, 0.5);
    vec3 c = vec3(1.0, 1.0, 1.0);
    vec3 d = vec3(0.263, 0.416, 0.557);
    
    return a + b * cos(6.28318 * (c * t + d));
}

void main() {
    vec2 uv = (gl_FragCoord.xy * 2.0 - resolution.xy) / resolution.y;
    vec2 uv0 = uv;
    vec3 finalColor = vec3(0.0);
    
    // Iteration loop to create layered effect
    for(float i = 0.0; i < 4.0; i++) {
        uv = fract(uv * 2.0) - 0.5;  // Original multiplier kept at 2.0
        float d = length(uv);
        
        // Modified color calculation with time-based animation
        vec3 col = palette(length(uv0) - time/2.0 + i*0.4);
        
        // Wave pattern generation
        d = sin(d * 8.0 - time) / 8.0;
        d = abs(d);
        d = pow(0.02 / d, 1.0);  // Adjusted to match original intensity
        
        finalColor += col * d;
    }
    
    gl_FragColor = vec4(finalColor, 1.0);
}