import sys
from ursina import Shader, Vec2, color, Entity, Ursina, Sky, EditorCamera, Vec3, held_keys, time

# Only define the shader on Android or Linux
if sys.platform in ('android', 'linux'):

    lit_with_shadows_shader_gles = Shader(
        language=Shader.GLSL,
        name='lit_with_shadows_shader',
        vertex='''
        #version 300 es
        precision highp float;

        uniform mat4 p3d_ModelViewProjectionMatrix;
        uniform mat4 p3d_ModelViewMatrix;
        uniform mat3 p3d_NormalMatrix;

        in vec4 vertex;
        in vec3 normal;
        in vec4 p3d_Color;
        in vec2 p3d_MultiTexCoord0;

        uniform vec2 texture_scale;
        uniform vec2 texture_offset;

        out vec2 texcoords;
        out vec3 vpos;
        out vec3 norm;
        out vec4 vertex_color;

        void main() {
            gl_Position = p3d_ModelViewProjectionMatrix * vertex;
            vpos = vec3(p3d_ModelViewMatrix * vertex);
            norm = normalize(p3d_NormalMatrix * normal);
            texcoords = (p3d_MultiTexCoord0 * texture_scale) + texture_offset;
            vertex_color = p3d_Color;
        }
        ''',
        fragment='''
        #version 300 es
        precision highp float;

        uniform sampler2D p3d_Texture0;
        uniform vec4 p3d_ColorScale;

        in vec2 texcoords;
        in vec3 vpos;
        in vec3 norm;
        in vec4 vertex_color;

        out vec4 p3d_FragColor;

        uniform vec4 shadow_color;

        void main() {
            vec3 N = normalize(norm);
            p3d_FragColor = texture(p3d_Texture0, texcoords) * p3d_ColorScale * vertex_color;

            // Simplified lighting for ES
            vec3 light_dir = normalize(vec3(1.0, -1.0, -1.0));  // simple directional light
            float NdotL = max(dot(N, light_dir), 0.0);
            vec3 diffuse = NdotL * vec3(1.0, 1.0, 1.0);  // white light

            vec3 converted_shadow_color = (vec3(1.0) - shadow_color.rgb) * shadow_color.a;

            p3d_FragColor.rgb *= diffuse;
            p3d_FragColor.rgb += converted_shadow_color;
        }
        ''',
        default_input={
            'texture_scale': Vec2(1, 1),
            'texture_offset': Vec2(0, 0),
            'shadow_color': color.rgba(0, 128, 255, 64 / 255),
        }
    )

# Example usage
if __name__ == '__main__':
    app = Ursina()

    if sys.platform in ('android', 'linux'):
        shader = lit_with_shadows_shader_gles
    else:
        shader = None  # fallback

    a = Entity(model='cube', shader=shader, y=1, color=color.light_gray)
    Entity(model='sphere', texture='shore', y=2, x=1, shader=shader)
    Entity(model='plane', scale=16, texture='grass', shader=shader)

    from ursina.lights import DirectionalLight
    sun = DirectionalLight(shadow_map_resolution=(1024, 1024))
    sun.look_at(Vec3(-1, -1, -10))

    Sky(color=color.light_gray)
    EditorCamera()

    def update():
        a.x += (held_keys['d'] - held_keys['a']) * time.dt * 5
        a.y += (held_keys['e'] - held_keys['q']) * time.dt * 5
        a.z += (held_keys['w'] - held_keys['s']) * time.dt * 5

    app.run()
