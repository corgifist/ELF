from direct.showbase.ShowBaseGlobal import globalClock

import elf

elf.elf_render_resolution(1280, 720)
elf.elf_fullscreen(True)
elf.elf_show_fps(True)
elf.elf_switch_to_legacy_pipeline(False)
elf.elf_init_show_base()
elf.elf_prefab_noclip()
elf.elf_camera_fov(90)
clouds = elf.elf_draw("models/plane.obj", scale=(4, 4, 4), position=(0, 10, 0), rotation=(-90, 0, 0))
gradient = elf.elf_draw("models/box", scale=(2, 2, 2), position=(15, 10, 0))
sky_texture = elf.elf_bind_texture("assets/clouds.png")
sky = elf.elf_draw("models/sky.obj", scale=(1000, 1000, 1000), rotation=(0, 90, 0))
elf.elf_attach_texture_to_id(sky, sky_texture)
elf.elf_attach_pipeline_effect(sky, "effects/skybox.yaml")
elf.elf_set_two_sided(sky, True)
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
