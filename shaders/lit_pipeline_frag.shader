#version 330

out vec4 outColor;

in vec2 texcoord;

uniform sampler2D p3d_Texture0;

void main() {

    outColor = texture(p3d_Texture0, texcoord);
}