#version 330
// Final pass over the internal-resolution frame: soft glow around bright things, ordered dithering with gentle
// colour banding (on the internal pixel grid, so it stays chunky), a light vignette, and optional screen effects:
// 1 Old TV (CRT), 2 VHS tape, 3 Fisheye, 4 Silent film, 5 Handheld (4-shade green LCD), 6 Noir,
// 7 Night vision, 8 Old computer (16-colour palette), 9 Tavern ale (drunk wobble).

in vec2 fragTexCoord;
in vec4 fragColor;

uniform sampler2D texture0;
uniform vec2 uTexel;       // 1 / internal resolution
uniform vec2 uScreen;      // on-screen size of the frame in pixels
uniform float uDither;     // 0 or 1
uniform float uGlow;       // 0..1
uniform float uVignette;   // 0..1
uniform int uEffect;       // 0 off
uniform float uTime;

out vec4 finalColor;

float hash(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }

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

// The scene at uv, with glow.
vec3 scene(vec2 uv)
{
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
        col += g / float(N) * uGlow;
    }
    return col;
}

vec2 barrel(vec2 uv, float k)
{
    vec2 c = uv * 2.0 - 1.0;
    c *= 1.0 + k * dot(c, c);
    return c * 0.5 + 0.5;
}

void main()
{
    vec2 uv = fragTexCoord;
    // The texture is drawn flipped; v grows upward. Work in screen space (0,0 top-left) for the effects.
    vec2 suv = vec2(uv.x, 1.0 - uv.y);
    vec2 spx = suv * uScreen;

    // --- Geometry: bend the picture
    if (uEffect == 1) suv = barrel(suv, 0.06);
    if (uEffect == 3) suv = barrel(suv, 0.32) * 0.86 + 0.07;
    if (uEffect == 2)  // VHS: line wobble and a rolling tracking band
    {
        float line = floor(spx.y / 2.0);
        suv.x += (hash(vec2(line, floor(uTime * 24.0))) - 0.5) * 0.0025;
        float band = fract(uTime * 0.07);
        float d = abs(suv.y - band);
        if (d < 0.035) suv.x += (hash(vec2(line, uTime)) - 0.5) * 0.03 * (1.0 - d / 0.035);
    }
    if (uEffect == 9)  // tavern ale: the room sways and breathes
    {
        vec2 c = suv - 0.5;
        float a = sin(uTime * 0.7) * 0.035;
        c = mat2(cos(a), -sin(a), sin(a), cos(a)) * c;
        c *= 1.0 + 0.03 * sin(uTime * 1.1);
        suv = c + 0.5 + vec2(sin(suv.y * 9.0 + uTime * 1.7), cos(suv.x * 7.0 + uTime * 1.3)) * 0.006;
    }
    if (uEffect == 4)  // film gate weave
        suv += vec2(sin(uTime * 7.0) * 0.0008, (hash(vec2(floor(uTime * 18.0), 3.0)) - 0.5) * 0.002);
    bool outside = suv.x < 0.0 || suv.x > 1.0 || suv.y < 0.0 || suv.y > 1.0;
    vec2 tuv = vec2(suv.x, 1.0 - suv.y);

    // Handheld: sample on a coarse ~144-line grid
    if (uEffect == 5)
    {
        vec2 grid = vec2(144.0 * uScreen.x / uScreen.y, 144.0);
        tuv = (floor(tuv * grid) + 0.5) / grid;
    }

    vec3 col;
    if (uEffect == 2)  // VHS: colour fringes and smeared chroma
    {
        float o = 0.0035;
        col = vec3(scene(tuv + vec2(o, 0.0)).r, scene(tuv).g, scene(tuv - vec2(o, 0.0)).b);
        vec3 smear = (scene(tuv - vec2(o * 2.0, 0.0)) + scene(tuv - vec2(o * 4.0, 0.0))) * 0.5;
        float y = dot(col, vec3(0.299, 0.587, 0.114));
        col = mix(vec3(y), mix(col, smear, 0.35), 0.82);
    }
    else if (uEffect == 9)  // double vision that drifts in and out
    {
        float o = 0.012 * (0.5 + 0.5 * sin(uTime * 0.9));
        col = mix(scene(tuv), scene(tuv + vec2(o, o * 0.4)), 0.4);
    }
    else
    {
        col = scene(tuv);
    }

    vec2 q = suv - 0.5;
    col *= 1.0 - uVignette * smoothstep(0.32, 0.85, dot(q, q) * 2.2);

    if (uDither > 0.0 && uEffect != 5 && uEffect != 8)
    {
        float cell = max(1.0, floor((1.0 / uTexel.y) / 360.0));
        vec2 px = floor(tuv / uTexel / cell);
        float levels = 22.0;
        col = floor(col * levels + bayer4(px)) / levels;
    }

    // --- Colour and texture of the medium
    if (uEffect == 1)  // Old TV
    {
        float scan = 0.78 + 0.22 * sin(spx.y * 3.14159 * 0.5);
        int m = int(mod(spx.x, 3.0));
        vec3 mask = m == 0 ? vec3(1.08, 0.92, 0.92) : (m == 1 ? vec3(0.92, 1.08, 0.92) : vec3(0.92, 0.92, 1.08));
        col = col * scan * mask * 1.18;
        col *= 0.97 + 0.03 * sin(uTime * 60.0);
        vec2 e = abs(suv - 0.5) * 2.0;
        col *= smoothstep(1.0, 0.9, max(e.x, e.y));   // rounded tube edge
    }
    else if (uEffect == 2)  // VHS
    {
        col += (hash(spx * 0.5 + uTime) - 0.5) * 0.08;
        float band = fract(uTime * 0.07);
        float d = abs(suv.y - band);
        if (d < 0.035) col += hash(vec2(spx.x * 0.1, uTime)) * 0.25 * (1.0 - d / 0.035);
        if (suv.y > 0.985) col = mix(col, vec3(hash(vec2(spx.x, uTime))), 0.6);  // head-switching noise
        col *= 0.92 + 0.08 * sin(spx.y * 1.2);
    }
    else if (uEffect == 3)  // Fisheye: dark lens rim
    {
        float r = length((suv - 0.5) * vec2(uScreen.x / uScreen.y, 1.0));
        col *= smoothstep(0.98, 0.72, r);
    }
    else if (uEffect == 4)  // Silent film
    {
        float y = dot(col, vec3(0.299, 0.587, 0.114));
        y = pow(y, 0.9) * (0.92 + 0.08 * hash(vec2(floor(uTime * 18.0), 1.0)));
        col = y * vec3(1.06, 0.97, 0.82);
        col += (hash(floor(spx / 2.0) + floor(uTime * 24.0)) - 0.5) * 0.12;
        float f = floor(uTime * 18.0);
        for (int i = 0; i < 2; i++)  // scratches
        {
            float sx = hash(vec2(f, float(i) * 7.0));
            if (hash(vec2(f, float(i) + 11.0)) > 0.55 && abs(suv.x - sx) < 0.0012) col = mix(col, vec3(0.95, 0.9, 0.8), 0.6);
        }
        if (hash(floor(spx / 3.0) + f) > 0.9993) col = vec3(0.05);   // dust
        col *= 1.0 - 0.6 * smoothstep(0.25, 0.9, dot(q, q) * 2.6);
    }
    else if (uEffect == 5)  // Handheld: four shades of green, LCD grid
    {
        float y = dot(col, vec3(0.299, 0.587, 0.114));
        vec2 cellpx = floor(tuv * vec2(144.0 * uScreen.x / uScreen.y, 144.0));
        y = clamp(y * 1.35 + (bayer4(cellpx) - 0.5) * 0.18, 0.0, 0.999);
        int s = int(y * 4.0);
        vec3 pal[4] = vec3[4](vec3(0.06, 0.22, 0.06), vec3(0.19, 0.38, 0.19), vec3(0.55, 0.67, 0.06), vec3(0.61, 0.74, 0.06));
        col = pal[s];
        vec2 lcd = fract(tuv * vec2(144.0 * uScreen.x / uScreen.y, 144.0));
        if (lcd.x < 0.08 || lcd.y < 0.08) col *= 0.88;
    }

    else if (uEffect == 6)  // Noir: hard black and white, crushed shadows, a little grain
    {
        float y = dot(col, vec3(0.299, 0.587, 0.114));
        y = smoothstep(0.06, 0.78, y);
        y = pow(y, 1.15) + (hash(floor(spx / 2.0) + floor(uTime * 20.0)) - 0.5) * 0.05;
        col = vec3(y) * vec3(1.0, 0.99, 0.96);
        col *= 1.0 - 0.7 * smoothstep(0.2, 0.85, dot(q, q) * 2.4);
    }
    else if (uEffect == 7)  // Night vision: amplified green, noise, scan bars, REC dot added on top by the renderer
    {
        float y = dot(col, vec3(0.299, 0.587, 0.114));
        y = clamp(y * 2.6 + 0.04, 0.0, 1.2);
        y += (hash(spx * 0.7 + fract(uTime) * 91.0) - 0.5) * 0.22;
        y *= 0.9 + 0.1 * sin(spx.y * 1.4 + uTime * 30.0);
        col = vec3(0.18, 1.0, 0.3) * y;
        float r = length((suv - 0.5) * vec2(uScreen.x / uScreen.y, 1.0));
        col *= smoothstep(0.95, 0.6, r);
    }
    else if (uEffect == 8)  // Old computer: snap to a 16-colour palette with dithering, chunky 200-line pixels
    {
        vec3 pal[16] = vec3[16](vec3(0.0), vec3(0.0, 0.0, 0.67), vec3(0.0, 0.67, 0.0), vec3(0.0, 0.67, 0.67),
                                vec3(0.67, 0.0, 0.0), vec3(0.67, 0.0, 0.67), vec3(0.67, 0.33, 0.0), vec3(0.67),
                                vec3(0.33), vec3(0.33, 0.33, 1.0), vec3(0.33, 1.0, 0.33), vec3(0.33, 1.0, 1.0),
                                vec3(1.0, 0.33, 0.33), vec3(1.0, 0.33, 1.0), vec3(1.0, 1.0, 0.33), vec3(1.0));
        vec2 grid = vec2(200.0 * uScreen.x / uScreen.y, 200.0);
        vec2 cellpx = floor(tuv * grid);
        vec3 c = scene((cellpx + 0.5) / grid);
        float l = dot(c, vec3(0.299, 0.587, 0.114));
        c = clamp(mix(vec3(l), c, 2.4) * 1.35, 0.0, 1.0) + (bayer4(cellpx) - 0.5) * 0.3;   // punchier, so greys pick hues
        float best = 1e9; vec3 pick = vec3(0.0);
        for (int i = 0; i < 16; i++) { vec3 d = c - pal[i]; float e = dot(d, d); if (e < best) { best = e; pick = pal[i]; } }
        col = pick;
    }
    else if (uEffect == 9)  // Tavern ale: warm, rosy, vignette breathing
    {
        col *= vec3(1.08, 0.98, 0.9);
        col *= 1.0 - (0.35 + 0.15 * sin(uTime * 1.2)) * smoothstep(0.2, 0.9, dot(q, q) * 2.4);
    }

    if (outside) col = vec3(0.0);
    finalColor = vec4(col, 1.0);
}
