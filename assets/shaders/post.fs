#version 330
// Final pass over the internal-resolution frame: soft glow around bright things, ordered dithering with gentle
// colour banding (on the internal pixel grid, so it stays chunky), and a light vignette.

in vec2 fragTexCoord;
in vec4 fragColor;

uniform sampler2D texture0;
uniform vec2 uTexel;       // 1 / internal resolution
uniform float uDither;     // 0 or 1
uniform float uGlow;       // 0..1
uniform float uVignette;   // 0..1

out vec4 finalColor;

float bayer4(vec2 px)
{
    int x = int(mod(px.x, 4.0)), y = int(mod(px.y, 4.0));
    int m[16] = int[16](0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5);
    return (float(m[y * 4 + x]) + 0.5) / 16.0;
}

vec3 bright(vec2 uv)
{
    vec3 c = texture(texture0, uv).rgb;
    float l = max(c.r, max(c.g, c.b));
    return c * smoothstep(0.62, 0.95, l);
}

void main()
{
    vec2 uv = fragTexCoord;
    vec3 col = texture(texture0, uv).rgb;

    if (uGlow > 0.0)
    {
        vec3 g = vec3(0.0);
        const int N = 12;
        for (int i = 0; i < N; i++)
        {
            float a = 6.2831853 * float(i) / float(N);
            vec2 d = vec2(cos(a), sin(a));
            g += bright(uv + d * uTexel * 2.5) * 0.6;
            g += bright(uv + d * uTexel * 6.0) * 0.4;
        }
        col += g / float(N) * 1.0 * uGlow;
    }

    vec2 q = uv - 0.5;
    col *= 1.0 - uVignette * smoothstep(0.32, 0.85, dot(q, q) * 2.2);

    if (uDither > 0.0)
    {
        // Keep the dither grid chunky (about 360 lines tall) even when rendering at native resolution.
        float cell = max(1.0, floor((1.0 / uTexel.y) / 360.0));
        vec2 px = floor(uv / uTexel / cell);
        float levels = 22.0;
        col = floor(col * levels + bayer4(px)) / levels;
    }
    finalColor = vec4(col, 1.0);
}
