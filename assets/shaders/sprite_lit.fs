#version 330

in vec3 fragPosition;
in vec2 fragTexCoord;
in vec4 fragColor;

uniform sampler2D texture0;
uniform vec4 colDiffuse;

#define MAX_LIGHTS 16
uniform int uLightCount;
uniform vec3 uLightPos[MAX_LIGHTS];
uniform vec3 uLightColor[MAX_LIGHTS];
uniform float uLightRadius[MAX_LIGHTS];

uniform vec3 uViewPos;
uniform vec3 uAmbientColor;
uniform vec3 uSunColor;
uniform vec3 uFogColor;
uniform float uFogDensity;
uniform float uEmissive;

out vec4 finalColor;

void main()
{
    vec4 texel = texture(texture0, fragTexCoord);
    if (texel.a < 0.5) discard;

    vec3 baseAlbedo = texel.rgb * colDiffuse.rgb * fragColor.rgb;

    // Sprites have no normals: flat ambient + half the sun + unshadowed point lights.
    vec3 totalLight = uAmbientColor * 1.05 + uSunColor * 0.35;
    for (int i = 0; i < uLightCount && i < MAX_LIGHTS; i++)
    {
        float dist = length(uLightPos[i] - fragPosition);
        float radius = max(uLightRadius[i], 0.1);
        if (dist < radius)
        {
            float atten = clamp(1.0 - (dist / radius), 0.0, 1.0);
            atten = atten * atten;
            float stepped = floor(atten * 6.0 + 0.5) / 6.0;
            totalLight += uLightColor[i] * mix(atten, stepped, 0.35) * 1.2;
        }
    }
    totalLight = max(totalLight, vec3(uEmissive));
    vec3 litColor = baseAlbedo * totalLight;

    float camDist = length(uViewPos - fragPosition);
    float fogFactor = clamp(exp(-pow(camDist * uFogDensity, 1.65)), 0.0, 1.0);

    finalColor = vec4(mix(uFogColor, litColor, fogFactor), texel.a * colDiffuse.a * fragColor.a);
}
