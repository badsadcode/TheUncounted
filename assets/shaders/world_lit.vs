#version 330

in vec3 vertexPosition;
in vec2 vertexTexCoord;
in vec3 vertexNormal;
in vec4 vertexColor;

uniform mat4 mvp;
uniform mat4 matModel;
uniform mat4 matNormal;
uniform vec2 uUvScale;

// World motion (set per model by the renderer; 0 = static)
uniform float uTime;
uniform float uSway;   // foliage: metres of sideways drift per metre of height
uniform float uWater;  // 1 = water: UVs from world position, slowly drifting
uniform float uWave;   // water: ripple height in metres; tentacles reuse it as a slow heave

out vec3 fragPosition;
out vec2 fragTexCoord;
out vec4 fragColor;
out vec3 fragNormal;

void main()
{
    vec3 p = vertexPosition;
    vec2 anchor = vec2(matModel[3][0], matModel[3][2]);   // the model's position: each tree sways out of step
    float phase = anchor.x * 0.37 + anchor.y * 0.23;
    if (uSway > 0.0)
    {
        float h = max(p.y, 0.0);
        float bend = pow(h, 1.35) * uSway;
        float gust = sin(uTime * 1.3 + phase) * 0.7 + sin(uTime * 2.9 + phase * 1.7) * 0.3;
        p.x += bend * gust;
        p.z += bend * 0.6 * cos(uTime * 1.1 + phase * 1.3);
    }
    vec4 worldPos = matModel * vec4(p, 1.0);
    if (uWave > 0.0)
    {
        float w = sin(worldPos.x * 0.9 + uTime * 1.6) * 0.6 + sin(worldPos.z * 1.3 - uTime * 1.1) * 0.4
                + sin((worldPos.x + worldPos.z) * 2.1 + uTime * 2.7) * 0.25;
        worldPos.y += w * uWave;
        p = (inverse(matModel) * worldPos).xyz;
    }
    fragPosition = worldPos.xyz;
    vec2 scale = (uUvScale.x > 0.001 && uUvScale.y > 0.001) ? uUvScale : vec2(1.0, 1.0);
    fragTexCoord = vertexTexCoord * scale;
    fragColor = vertexColor;
    if (uWater > 0.5)
    {
        fragTexCoord = worldPos.xz / 3.2 + vec2(uTime * 0.025, uTime * 0.012);
        fragColor = mix(vertexColor, vec4(1.0), 0.75);
    }
    fragNormal = normalize(vec3(matNormal * vec4(vertexNormal, 0.0)));
    gl_Position = mvp * vec4(p, 1.0);
}
