#version 330

in vec4 p3d_Vertex;

out vec3 pos;

uniform mat4 p3d_ModelViewProjectionMatrix;

void main() {
    gl_Position = p3d_Vertex * p3d_ModelViewProjectionMatrix;
    pos = gl_Position;
}