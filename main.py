from direct.showbase.ShowBaseGlobal import globalClock

import elf

elf.elf_show_fps(True)
elf.elf_init_show_base()
elf.elf_enable_mouse()
shader = elf.elf_parse_glsl("shaders/shadertoy_fog_vert.shader", "shaders/shadertoy_fog_frag.shader")
triangle = elf.elf_draw("models/plane.obj", scale=(3, 3.6, 2.7), position=(0, 10, 0), rotation=(-90, 0, 0))


def update(task):
    elf.elf_set_in_glsl(triangle, "iTime", globalClock.getFrameTime())
    return task.cont


def win_resize(task):
    elf.elf_set_in_glsl(triangle, "iResolution", (elf.elf_win_w(), elf.elf_win_h()))
    elf.elf_set_in_glsl(triangle, "iMouse", (elf.elf_win_w() / 2, elf.elf_win_h() / 2))
    return task.cont


elf.elf_add_task(win_resize, "aspectRatioChanged")
elf.elf_attach_shader_to_model(triangle, shader)
elf.elf_set_update(update)
elf.elf_render_window()
