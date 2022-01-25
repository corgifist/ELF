from random import randint, random

from panda3d.core import AntialiasAttrib, loadPrcFileData
from rpcore import RenderPipeline
from ursina import *
from ursina.shaders import *

app = Ursina()
pipeline = RenderPipeline()

ELF_COLOR = color.white
ELFC = color
ELF_SIMPLE_TRIANGLE = ['triangle.obj', (0, 0, 0), (0.5, 0.5, 0.5), (0, 0, 0)]
ELF_MAP = {}
ELF_LAST_ID = -1
update = None

ELF_TEST_PARENT_ID = -1


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
    loadPrcFileData('', 'win-size ' + str(context.w) + ' ' + str(context.h))


def elf_begin_color(color_constant):
    global ELF_COLOR
    ELF_COLOR = color_constant


def elf_end_color():
    global ELF_COLOR
    ELF_COLOR = color.white


def elf_draw(obj, receive_shadows=True):
    shape = obj[0]
    pos = obj[1]
    sc = obj[2]
    rot = obj[3]
    en_id = elf_gen_id()
    ELF_MAP[en_id] = Entity(model=shape, position=pos, scale=sc, rotation=rot, color=ELF_COLOR)
    if receive_shadows:
        ELF_MAP[en_id].shader = basic_lighting_shader
    return en_id


def elf_draw_parent(parent, obj, receive_shadows=True):
    shape = obj[0]
    pos = obj[1]
    sc = obj[2]
    rot = obj[3]
    en_id = elf_gen_id()
    entity = Entity(model=shape, position=pos, scale=sc, rotation=rot, color=ELF_COLOR, parent=ELF_MAP[parent])
    if receive_shadows:
        entity.shader = basic_lighting_shader
    return en_id


def elf_draw_empty():
    en_id = elf_gen_id()
    ELF_MAP[en_id] = Entity()
    return en_id


def elf_render_window():
    app.run()


def elf_clear_back():
    en_id = elf_gen_id()
    ELF_MAP[en_id] = Sky(color=color.black)


def elf_gen_id():
    global ELF_LAST_ID
    ELF_LAST_ID = randint(0, 100000000000000000000)
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


def elf_set_render(uf):
    global update
    update = uf


def elf_shade_dir_light(object, enable_shadows=True, resolution=1024):
    rot = (object[0], object[1], object[2])
    dir_light = DirectionalLight(rotation=rot)
    obj_id = elf_gen_id()
    dir_light.light.setShadowCaster(enable_shadows, resolution, resolution)
    dir_light.setShaderAuto()
    ELF_MAP[obj_id] = dir_light
    return obj_id


def elf_gen_dir_light(object, enable_shadows=True, resolution=1024):
    en_id = elf_gen_id()
    rot = (object[0], object[1], object[2])
    dir_light = DirectionalLight(rotation=rot, shadows=enable_shadows)
    dir_light.light.setShadowCaster(enable_shadows, resolution, resolution)
    ELF_MAP[en_id] = dir_light
    return dir_light


def elf_attach_light_to_id(id, light):
    light.position = ELF_MAP[id].position
    return id


def elf_shade_point_light(object, enable_shadows=True, at=(0, 0, 1), resolution=1024):
    pos = (object[0], object[1], object[2])
    en_id = elf_gen_id()
    point_light = PointLight(shadows=True)
    point_light.pos = pos
    point_light.casts_shadows = enable_shadows
    point_light.attenuation = at
    point_light.light.setShadowCaster(enable_shadows, resolution, resolution)
    ELF_MAP[en_id] = point_light
    return en_id


def elf_gen_point_light(object, enable_shadows=True, at=(0, 0, 1), resolution=1024):
    en_id = elf_gen_id()
    pos = (object[0], object[1], object[2])
    point_light = PointLight()
    point_light.pos = pos
    point_light._light.setShadowCaster(enable_shadows, resolution, resolution)
    point_light.attenuation = at
    ELF_MAP[en_id] = point_light
    return point_light


def elf_antialiasing_enable():
    for key in ELF_MAP:
        try:
            ELF_MAP[key].setAntialias(AntialiasAttrib.MAuto)
        except Exception:
            pass
    print("ELF: Antialiasing success")


def elf_space_reset():
    for key in ELF_MAP:
        ELF_MAP[key].enabled = False
    ELF_MAP.clear()
    elf_clear_back()


def elf_random_color():
    return color.random_color()


def gen_triangles():
    for i in range(150):
        elf_begin_color(elf_random_color())
        scale = (0.5, 0.5, 0.5)
        rotation = (randint(0, 360), randint(0, 360), randint(0, 360),)
        position = (random.uniform(-7, 10), random.uniform(-5, 6), random.uniform(-20, 20))
        elf_draw_parent(ELF_TEST_PARENT_ID, ["triangle", position, scale, rotation])
        elf_end_color()
    elf_attach_light_to_id(ELF_TEST_PARENT_ID, elf_gen_point_light([0, 0, 0]))


def elf_input(key):
    return held_keys[key]


def elf_begin_wireframe():
    for key in ELF_MAP:
        ELF_MAP[key].setRenderModeWireframe(True)


def elf_end_wireframe():
    for key in ELF_MAP:
        ELF_MAP[key].setRenderModeWireframe(False)


def elf_shift_space(x, y, z):
    for key in ELF_MAP:
        ELF_MAP[key].x += x
        ELF_MAP[key].y += y
        ELF_MAP[key].z += z


def elf_load_identity():
    for key in ELF_MAP:
        ELF_MAP[key].x += 0
        ELF_MAP[key].y += 0
        ELF_MAP[key].z += 0


def elf_matrix_rotate_space(x, y, z):
    for key in ELF_MAP:
        ELF_MAP[key].rotation_x += x
        ELF_MAP[key].rotation_y += y
        ELF_MAP[key].rotation_z += z


def elf_shift_camera_matrix(x, y, z):
    camera.x += x
    camera.y += y
    camera.z += z


def elf_rotate_camera_matrix(x, y, z):
    camera.rotation_x += x
    camera.rotation_y += y
    camera.rotation_z += z


def elf_update():
    if elf_input('r'):
        elf_space_reset()
        draw_triangles()
        return
    if elf_input('w'):
        elf_shift_camera_matrix(0, 0, 0.1)
    elif elf_input('s'):
        elf_shift_camera_matrix(0, 0, -0.1)
    elif elf_input('d'):
        elf_shift_camera_matrix(0.1, 0, 0)
    elif elf_input('a'):
        elf_shift_camera_matrix(-0.1, 0, 0)
    elif elf_input('down arrow'):
        elf_rotate_camera_matrix(0.1, 0, 0)
    elif elf_input('up arrow'):
        elf_rotate_camera_matrix(-0.1, 0, 0)
    elif elf_input('right arrow'):
        elf_rotate_camera_matrix(0, 0.2, 0)
    elif elf_input('left arrow'):
        elf_rotate_camera_matrix(0, -0.2, 0)
    elif elf_input('left shift'):
        elf_shift_camera_matrix(0, 0.1, 0)
    elif elf_input('space'):
        elf_shift_camera_matrix(0, -0.1, 0)


def elf_shader_generation():
    app.render.setShaderAuto(True)


def main():
    context = elf_create_context()
    elf_clear_back()
    elf_prepare_context(context)
    draw_triangles()
    elf_set_render(elf_update)
    elf_shader_generation()
    elf_antialiasing_enable()
    elf_render_window()


def draw_triangles():
    global ELF_TEST_PARENT_ID
    ELF_TEST_PARENT_ID = elf_draw(["triangle", (0, 0, 0), (0.5, 0.5, 0.5), (0, 0, 0)])
    gen_triangles()


if __name__ == '__main__':
    main()
