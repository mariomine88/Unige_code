precision highp float;
uniform vec2 u_resolution;

void main()
{
    // Normalized pixel coordinates (from 0 to 1)
    vec2 uv = gl_FragCoord.xy/u_resolution;

    // Define a color (RG only)
    vec2 col = uv.xy;

    // Output to screen
    gl_FragColor = vec4(col,1.0-length(col),1.0);
}