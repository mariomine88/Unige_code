void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    // Normalized pixel coordinates (from 0 to 1)
    vec2 uv = fragCoord/iResolution.xy;

    // Define a color (RG only)
    vec2 col = uv.xy;

    // Output to screen
    fragColor = vec4(col,1.0-length(col),1.0);
}