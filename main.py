import elf

elf.elf_switch_to_legacy_pipeline(True)
elf.elf_init_show_base()
elf.elf_prefab_noclip()
elf.elf_camera_fov(90)
elf.elf_daytime_manager(0.0)
env = elf.elf_draw("models/environment", scale=(0.3, 0.3, 0.3), panda3d_fix=True)
light = elf.elf_shade_point_light(position=(0, -50, 20), color=(10000, 10000, 10000), energy=400)
elf.elf_draw("models/box", parent=light, scale=(10, 10, 10), color=(1, 1, 1))
elf.elf_change_skybox("assets/clouds.png")
elf.elf_render_window()
