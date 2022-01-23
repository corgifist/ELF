from ursina import *
from random import randint

app = Ursina()

ELF_COLOR = color.white
ELFC = color
ELF_SIMPLE_TRIANGLE = ['triangle.obj', (0, 0, 0), (0.5, 0.5, 0.5), (0, 0, 0)]
ELF_MAP = {}
ELF_LAST_ID = -1
update = None

ELF_TEST_TRIANGLE_ID = -1


class ELFContext:
    def __init__(self, t, w, h, f, b):
        self.t = t
        self.w = w
        self.h = h
        self.f = f
        self.b = b


def elf_create_context(title='ELF', w=1920, h=1080, fps=False, borderless=False):
    return ELFContext(title, w, h, fps, borderless)


def elf_prepare_context(context):
    window.title = context.t
    window.borderless = context.b
    window.setSize(context.w, context.h)
    window.fps_counter.enabled = context.f
    window.exit_button.enabled = False


def elf_begin_color(color_constant):
    global ELF_COLOR
    ELF_COLOR = color_constant


def elf_end_color():
    global ELF_COLOR
    ELF_COLOR = color.white


def elf_draw(obj):
    shape = obj[0]
    pos = obj[1]
    sc = obj[2]
    rot = obj[3]
    en_id = elf_gen_id()
    ELF_MAP[en_id] = Entity(model=shape, position=pos, scale=sc, rotation=rot, color=ELF_COLOR)
    return en_id


def elf_render_window():
    app.run()


def elf_clear_back():
    en_id = elf_gen_id()
    ELF_MAP[en_id] = Sky(color=color.black)


def elf_gen_id():
    global ELF_LAST_ID
    ELF_LAST_ID = randint(0, 1000000000000000000)
    return ELF_LAST_ID


# Translation + Rotation

def elf_translate_space_by_id(id, x, y, z):
    ELF_MAP[id].x += x
    ELF_MAP[id].y += y
    ELF_MAP[id].z += z


def elf_translate_space(x, y, z):
    elf_translate_space_by_id(ELF_LAST_ID, x, y, z)


def elf_rotate_space_by_id(id, x, y, z):
    ELF_MAP[id].rotation_x += x
    ELF_MAP[id].rotation_y += y
    ELF_MAP[id].rotation_z += z


def elf_rotate_space(x, y, z):
    elf_rotate_space_by_id(ELF_LAST_ID, x, y, z)


def elf_update():
    elf_translate_space_by_id(ELF_TEST_TRIANGLE_ID, 0, 0, -0.01)
    elf_rotate_space_by_id(ELF_TEST_TRIANGLE_ID, 0, 1, 0)


def elf_set_render(uf):
    global update
    update = uf

def elf_shade_dir_light(object, enable_shadows=True):
    rot = (object[0], object[1], object[2])
    dir_light = DirectionalLight(rotation=rot, shadows=enable_shadows)
    obj_id = elf_gen_id()
    ELF_MAP[obj_id] = dir_light
    return obj_id


def main():
    global ELF_TEST_TRIANGLE_ID
    context = elf_create_context()
    elf_clear_back()
    elf_prepare_context(context)
    elf_begin_color(ELFC.yellow)
    ELF_TEST_TRIANGLE_ID = elf_draw(ELF_SIMPLE_TRIANGLE)
    elf_shade_dir_light([0, 0, 0])
    elf_set_render(elf_update)
    elf_render_window()


if __name__ == '__main__':
    main()
