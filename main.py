import elf

elf.elf_switch_to_legacy_pipeline(True)
elf.elf_init_show_base()
elf.elf_prefab_noclip()
elf.elf_camera_fov(90)
normal_panda = elf.elf_draw("models/panda", scale=(0.2, 0.2, 0.2))
lit_panda = elf.elf_draw("models/panda", scale=(0.2, 0.2, 0.2), position=(4, 0, 0), use_lit_pipeline=True)
raw_color_panda = elf.elf_draw("models/panda", scale=(0.2, 0.2, 0.2), position=(8, 0, 0), color=(1, 0, 0))
wireframe_panda = elf.elf_draw("models/panda", scale=(0.2, 0.2, 0.2), position=(12, 0, 0), wireframe=True)
rotating_panda = elf.elf_draw("models/panda", scale=(0.2, 0.2, 0.2), position=(16, 0, 0), use_lit_pipeline=True)


def update(task):
    elf.elf_rotate_object(rotating_panda, 1, 1, 1)
    return task.cont


elf.elf_change_skybox("assets/clouds.png")
elf.elf_set_update(update)
elf.elf_render_window()
