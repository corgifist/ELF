from direct.showbase.ShowBaseGlobal import globalClock

import elf

elf.elf_show_fps(True)
elf.elf_init_show_base()
elf.elf_prefab_noclip()
clouds = elf.elf_draw("models/plane.obj", scale=(4, 4, 4), position=(0, 10, 0), rotation=(-90, 0, 0))
gradient = elf.elf_draw("models/box", scale=(2, 2, 2), position=(15, 10, 0))
elf.elf_attach_pipeline_effect(gradient, "shaders/easy_gradient.yaml")
elf.elf_attach_pipeline_effect(clouds, "shaders/shadertoy_fog.yaml")


def update(task):
    elf.elf_set_in_glsl(clouds, "iTime", globalClock.getFrameTime())
    return task.cont


def win_resize(task):
    elf.elf_set_in_glsl(clouds, "iResolution", (elf.elf_win_w(), elf.elf_win_h()))
    elf.elf_set_in_glsl(clouds, "iMouse", (elf.elf_win_w() / 2, elf.elf_win_h() / 2))
    return task.cont


elf.elf_add_task(win_resize, "aspectRatioChanged")
elf.elf_set_update(update)
elf.elf_render_window()
