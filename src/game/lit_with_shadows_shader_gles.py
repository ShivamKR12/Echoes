# Do not remove these lines
from setup_ursina_android import setup_ursina_android
setup_ursina_android()

import sys
from ursina import *

from panda3d.core import loadPrcFileData
loadPrcFileData("", "notify-level-glgsg debug")
loadPrcFileData("", "notify-level-shader debug")
loadPrcFileData("", "notify-level-texture debug")

# Only define the shader on Android or Linux
if sys.platform in ('android', 'linux'):
    print("Defining lit_with_shadows_shader_gles for platform:", sys.platform)

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

    print("Current platform:", sys.platform)

    if sys.platform in ('android', 'linux'):
        print("Using lit_with_shadows_shader_gles")
        shader = lit_with_shadows_shader_gles
    else:
        shader = None  # fallback

    a = Entity(model='cube', shader=shader, y=1, color=color.light_gray)
    Entity(model='sphere', texture='../ursina_assets/shore', y=2, x=1, shader=shader)
    Entity(model='plane', scale=16, texture='../ursina_assets/grass', shader=shader)

    print("Shader Inputs:")
    print("texture:", a.texture)
    print("color:", a.color)
    print("Shader active:", a.shader)
    print("shader:", shader)

    from ursina.lights import DirectionalLight
    sun = DirectionalLight(shadow_map_resolution=(1024, 1024))
    sun.look_at(Vec3(-1, -1, -10))

    Sky(color=color.light_gray)
    EditorCamera()

    def update():
        if mouse.left and mouse.hovered_entity and isinstance(mouse.hovered_entity, Button):
            return

    app.run()
