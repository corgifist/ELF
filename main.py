import elf

elf.elf_init_show_base()
elf.elf_draw("models/triangle.obj", coords=(0, 10, -1), scale=(0.2, 0.2, 0.2))
elf.elf_render_window()