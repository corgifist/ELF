from random import randint, random

from panda3d.core import AntialiasAttrib, loadPrcFileData, Material, Fog
from direct.filter.CommonFilters import CommonFilters
from ursina import *
from ursina.shaders import *

loadPrcFileData("", "parallax-mapping-samples 3")
loadPrcFileData("", "parallax-mapping-scale 0.1")

app = Ursina()
filters = None

ELF_COLOR = color.white
ELFC = color
ELF_SIMPLE_TRIANGLE = ['triangle.obj', (0, 0, 0), (0.5, 0.5, 0.5), (0, 0, 0)]
ELF_MAP = {}
ELF_PARENTS = {}
ELF_MATERIALS = {}
ELF_LAST_ID = -1
update = None
ELF_SKY = None

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


def elf_draw(obj, receive_shadows=True, material_id=-1, culling=True):
    shape = obj[0]
    pos = obj[1]
    sc = obj[2]
    rot = obj[3]
    en_id = elf_gen_id()
    ELF_MAP[en_id] = Entity(model=shape, position=pos, scale=sc, rotation=rot, color=ELF_COLOR)
    if not receive_shadows:
        ELF_MAP[en_id].setShaderAuto(False)
    if material_id != -1:
        ELF_MAP[en_id].setMaterial(ELF_MATERIALS[material_id])
    ELF_MAP[en_id].setTwoSided(not culling)
    return en_id


def elf_draw_parent(parent, obj, receive_shadows=True, material_id=-1, culling=True):
    shape = obj[0]
    pos = obj[1]
    sc = obj[2]
    rot = obj[3]
    en_id = elf_gen_id()
    entity = Entity(model=shape, position=pos, scale=sc, rotation=rot, color=ELF_COLOR, parent=ELF_MAP[parent])
    if receive_shadows:
        entity.shader = basic_lighting_shader
    if material_id != -1:
        entity.setMaterial(ELF_MATERIALS[material_id])
    entity.setTwoSided(not culling)
    ELF_PARENTS[parent] = ELF_PARENTS[parent] + [entity] if parent in ELF_PARENTS else [entity]
    return en_id


def elf_draw_empty():
    en_id = elf_gen_id()
    ELF_MAP[en_id] = Entity()
    return en_id


def elf_render_window():
    app.run()


def elf_filters_bloom():
    filters.setBloom()


def elf_clear_back():
    en_id = elf_gen_id()
    global ELF_SKY
    ELF_SKY = Sky(color=color.black)


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


def elf_render_exp_fog(color=(0.5, 0.5, 0.5, 1), exp=1.0):
    en_id = elf_gen_id()
    fog = Fog('expfog')
    fog.setColor(color)
    fog.setExpDensity(exp)
    app.render.setFog(fog)
    ELF_MAP[en_id] = fog
    return en_id


def elf_render_linear_fog(color=(0.5, 0.5, 0.5, 1), linear_range_start=0, linear_range_end=160, fallback1=45,
                          fallback2=160, fallback3=320):
    en_id = elf_gen_id()
    fog = Fog('expfog')
    fog.setColor(color)
    fog.setLinearRange(linear_range_start, linear_range_end)
    fog.setLinearFallback(fallback1, fallback2, fallback3)
    app.render.setFog(fog)
    ELF_MAP[en_id] = fog
    return en_id


def elf_reset_fog():
    app.render.clearFog()


def elf_gen_point_light(object, enable_shadows=True, at=(0, 0, 1), resolution=1024):
    en_id = elf_gen_id()
    pos = (object[0], object[1], object[2])
    point_light = PointLight()
    point_light.pos = pos
    point_light._light.setShadowCaster(enable_shadows, resolution, resolution)
    point_light.attenuation = at
    ELF_MAP[en_id] = point_light
    return point_light


def elf_shade_ambient(color=(0.4, 0.4, 0.4, 0.4)):
    en_id = elf_gen_id()
    ambient_light = AmbientLight(color=color)
    ELF_MAP[en_id] = ambient_light
    return en_id


def elf_antialiasing_enable():
    app.render.setAntialias(AntialiasAttrib.M_always)
    print("ELF: Antialiasing success")


def elf_culling_control(id, culling):
    ELF_MAP[id].setTwoSided(not culling)


def elf_global_culling_control(culling):
    for key in ELF_MAP:
        elf_culling_control(key, culling)


def elf_space_reset():
    for key in ELF_MAP:
        ELF_MAP[key].enabled = False
    ELF_MAP.clear()
    elf_clear_back()


def elf_random_color():
    return color.random_color()


def gen_material():
    id = elf_gen_material()
    elf_material_set_emmision_id(id, (0, 0, 0, 1))
    return id


def gen_triangles():
    material_id = gen_material()
    for i in range(150):
        elf_begin_color(elf_random_color())
        scale = (0.5, 0.5, 0.5)
        rotation = (randint(0, 360), randint(0, 360), randint(0, 360),)
        position = (random.uniform(-7, 10), random.uniform(-5, 6), random.uniform(-20, 20))
        elf_draw_parent(ELF_TEST_PARENT_ID, ["triangle.obj", position, scale, rotation], material_id=material_id)
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


def elf_change_model_by_id(id, model):
    ELF_MAP[id].model = model


def elf_change_model(model):
    ELF_MAP[ELF_LAST_ID] = model


# Materials

def elf_gen_material():
    material = Material()
    en_id = elf_gen_id()
    ELF_MATERIALS[en_id] = material
    return en_id


def elf_material_set_shininess_id(id, value):
    ELF_MATERIALS[id].setShininess(value)
    return id


def elf_material_set_specular_id(id, rgba):
    ELF_MATERIALS[id].setSpecular(rgba)
    return id


def elf_material_set_deffuse_id(id, rgba):
    ELF_MATERIALS[id].setDiffuse(rgba)
    return id


def elf_material_set_emmision_id(id, rgba):
    ELF_MATERIALS[id].setEmission(rgba)
    return id


def elf_material_apply(obj, mat):
    ELF_MAP[obj].setMaterial(ELF_MATERIALS[mat])


def elf_material_set_ambient_id(id, rgba):
    ELF_MATERIALS[id].setAmbient(rgba)
    return id


# Materials


def elf_update():
    elf_rotate_space_by_id(ELF_TEST_PARENT_ID, 0, 0.2, 0)
    if elf_input('r'):
        elf_space_reset()
        draw_triangles()
        return
    if elf_input('w'):
        elf_shift_camera_matrix(0, 0, 0.1)
    if elf_input('s'):
        elf_shift_camera_matrix(0, 0, -0.1)
    if elf_input('d'):
        elf_shift_camera_matrix(0.1, 0, 0)
    if elf_input('a'):
        elf_shift_camera_matrix(-0.1, 0, 0)
    if elf_input('down arrow'):
        elf_rotate_camera_matrix(0.1, 0, 0)
    if elf_input('up arrow'):
        elf_rotate_camera_matrix(-0.1, 0, 0)
    if elf_input('right arrow'):
        elf_rotate_camera_matrix(0, 0.3, 0)
    if elf_input('left arrow'):
        elf_rotate_camera_matrix(0, -0.3, 0)
    if elf_input('left shift'):
        elf_shift_camera_matrix(0, 0.1, 0)
    if elf_input('space'):
        elf_shift_camera_matrix(0, -0.1, 0)
    if elf_input('q'):
        for key in ELF_MAP:
            elf_change_model_by_id(key, "cube")
        for key in ELF_PARENTS:
            for child in ELF_PARENTS[key]:
                child.model = "cube"
        elf_clear_back()


def elf_shader_generation():
    app.render.setShaderAuto(True)


def main():
    global filters
    filters = CommonFilters(app.win, app.cam)
    filters.reconfigure(True, True)
    filters.set_ambient_occlusion = True
    context = elf_create_context()
    elf_clear_back()
    elf_prepare_context(context)
    elf_shade_ambient(color=(0.2, 0.2, 0.2, 0.2))
    draw_triangles()
    elf_set_render(elf_update)
    elf_shader_generation()
    elf_antialiasing_enable()
    elf_render_linear_fog()
    elf_render_window()


def draw_triangles():
    global ELF_TEST_PARENT_ID
    elf_begin_color(ELFC.white)
    ELF_TEST_PARENT_ID = elf_draw(["triangle", (0, 0, 0), (0.5, 0.5, 0.5), (0, 0, 0)], receive_shadows=False)
    elf_end_color()
    gen_triangles()


if __name__ == '__main__':
    main()
