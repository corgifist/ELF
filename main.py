import random

import elf

elf.elf_switch_to_legacy_pipeline(True)
elf.elf_init_show_base()
elf.elf_prefab_noclip()
elf.elf_camera_fov(90)
elf.elf_daytime_manager(12.00)


def update():
    elf.elf_rotate_object(parent_triangle, 0.1, 0, 0)


def reload():
    elf.elf_clear_space()
    global parent_triangle
    parent_triangle = elf.elf_draw("models/triangle.obj", color=(0, 1, 1), rotation=(0, 0, 0))
    for i in range(150):
        scale = (0.5, 0.5, 0.5)
        rotation = (random.randint(0, 360), 0, random.randint(0, 360),)
        position = (random.uniform(-7, 10), random.uniform(-5, 6), random.uniform(-20, 20))
        elf.elf_draw("models/triangle.obj", position=position, rotation=rotation, scale=scale,
                     color=(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)), parent=parent_triangle)

    elf.elf_rotate_object(parent_triangle, 0, 90, 0)
    elf.elf_shade_point_light(color=(10, 10, 10), energy=100)
    elf.elf_shade_ambient_light(color=(0.2, 0.2, 0.2))

reload()
elf.elf_accept("r", reload)
elf.elf_set_update(update)
elf.elf_change_skybox("assets/clouds.png")
elf.elf_render_window()
