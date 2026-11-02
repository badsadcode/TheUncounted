#version 330

in vec3 fragPosition;
in vec2 fragTexCoord;
in vec4 fragColor;
in vec3 fragNormal;

uniform sampler2D texture0;
uniform vec4 colDiffuse;

#define MAX_LIGHTS 16
uniform int uLightCount;
uniform vec3 uLightPos[MAX_LIGHTS];
uniform vec3 uLightColor[MAX_LIGHTS];
uniform float uLightRadius[MAX_LIGHTS];

uniform vec3 uViewPos;
uniform vec3 uAmbientColor;
uniform vec3 uSunDir;
uniform vec3 uSunColor;
uniform vec3 uFogColor;
uniform float uFogDensity;
uniform float uEmissive;

out vec4 finalColor;

void main()
{
    vec4 texel = texture(texture0, fragTexCoord);
    if (texel.a < 0.1) discard;

    vec3 baseAlbedo = texel.rgb * colDiffuse.rgb * fragColor.rgb;
    vec3 N = normalize(fragNormal);

    // Hemisphere + directional sun lighting
    vec3 sunDir = normalize(uSunDir);
    float ndotl = max(dot(N, sunDir), 0.0);
    float hemi = 0.5 + 0.5 * N.y;
    vec3 totalLight = uAmbientColor * mix(0.75, 1.15, hemi) + uSunColor * (ndotl * 0.65);

    // Dynamic point lights (torches, rune crystals, Glimmer spell, projectiles)
    for (int i = 0; i < uLightCount && i < MAX_LIGHTS; i++)
    {
        vec3 toLight = uLightPos[i] - fragPosition;
        float dist = length(toLight);
        float radius = max(uLightRadius[i], 0.1);
        if (dist < radius)
        {
            vec3 L = toLight / max(dist, 0.0001);
            float atten = clamp(1.0 - (dist / radius), 0.0, 1.0);
            atten = atten * atten;
            // Retro pixel-art stepped attenuation band + soft falloff
            float stepped = floor(atten * 6.0 + 0.5) / 6.0;
            float mixAtten = mix(atten, stepped, 0.35);
            float diff = max(dot(N, L), 0.25);
            totalLight += uLightColor[i] * diff * mixAtten * 1.45;
        }
    }

    totalLight = max(totalLight, vec3(uEmissive));
    vec3 litColor = baseAlbedo * totalLight;

    // Exponential squared distance fog
    float camDist = length(uViewPos - fragPosition);
    float fogFactor = exp(-pow(camDist * uFogDensity, 1.65));
    fogFactor = clamp(fogFactor, 0.0, 1.0);

    vec3 outRgb = mix(uFogColor, litColor, fogFactor);
    finalColor = vec4(outRgb, texel.a * colDiffuse.a * fragColor.a);
}
