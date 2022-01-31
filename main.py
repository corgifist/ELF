import elf

elf.elf_switch_to_legacy_pipeline(True)
elf.elf_init_show_base()
elf.elf_prefab_noclip()
elf.elf_camera_fov(90)
elf.elf_daytime_manager(0.0)
env = elf.elf_draw("models/environment", scale=(0.3, 0.3, 0.3), panda3d_fix=True)
light = elf.elf_shade_point_light(position=(0, -75, 20), color=(10000, 10000, 10000), energy=400)
box = elf.elf_draw("models/box", scale=(10, 10, 10), panda3d_fix=True)
elf.elf_runtime_attach_model(light, box)
elf.elf_shade_ambient_light(color=(0.2, 0.2, 0.2))
back = False
print(elf.ELF_SHOW_BASE.pipe.getInterfaceName())


def update():
    light_pos = elf.elf_get_pos(light)
    global back
    coord = abs(light_pos[1])
    if coord >= 50 and not back:
        if int(coord) == 50:
            back = True
            return
        elf.elf_translate_object(light, 0, 0.1, 0)
    if coord <= 75 and back:
        if coord == 75:
            back = False
            return
        elf.elf_translate_object(light, 0, -0.1, 0)


elf.elf_set_update(update)
elf.elf_change_skybox("assets/clouds.png")
elf.elf_render_window()
