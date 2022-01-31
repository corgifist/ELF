import random

import imgui.integrations.opengl

from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData, ConfigVariableManager, Shader, Material, PointLight, DirectionalLight, \
    AmbientLight, NodePath
from direct.filter.CommonFilters import CommonFilters
from rpcore import RenderPipeline
from rpcore import PointLight as RP_PointLight
from rpcore.util.movement_controller import MovementController

import elf


class ELF_RUNTIME(ShowBase):
    def __init__(self):
        global ELF_PIPELINE
        if not ELF_PIPELINE_FLAG:
            super().__init__()
        else:
            ELF_PIPELINE = RenderPipeline()
            ELF_PIPELINE.set_loading_screen_image("assets/splash.jpg")
            ELF_PIPELINE.create(self)

    def update(self, task):
        pass


ELF_SHOW_BASE: ELF_RUNTIME = None
ELF_OBJECTS = {}
ELF_SHADERS = {}
ELF_TEXTURES = {}
ELF_PIPELINE: RenderPipeline = None
ELF_FILTERS: CommonFilters = None
ELF_PIPELINE_FLAG = True
ELF_SKYBOX_ID = -1
ELF_ATTACHES: [NodePath, NodePath] = {}
ELF_UPDATE = None
ELF_LAST_SKY = None


def elf_enable_mouse():
    ELF_SHOW_BASE.enableMouse()


def elf_switch_to_legacy_pipeline(flag):
    global ELF_PIPELINE_FLAG
    if ELF_SHOW_BASE != None:
        print("Can't switch to legacy pipeline, because ShowBase is ready to use.\nPlease use "
              "'elf_switch_to_legacy_pipeline' before initializing ShowBase!")
    ELF_PIPELINE_FLAG = not flag


def elf_init_show_base():
    global ELF_SHOW_BASE, ELF_UPDATE
    elf_win_title('ELF')
    elf_use_assimp()
    ELF_SHOW_BASE = ELF_RUNTIME()
    ELF_SHOW_BASE.disableMouse()
    if not ELF_PIPELINE_FLAG:
        ELF_SHOW_BASE.render.setShaderAuto(True)


def elf_win_size(w, h):
    if ELF_SHOW_BASE != None:
        print("ELF: failed to change win-size because this function is special, and needs to be called before "
              "'elf_init_show_base'")
    loadPrcFileData('', 'win-size ' + str(w) + ' ' + str(h))


def elf_win_title(title):
    if ELF_SHOW_BASE != None:
        print("ELF: failed to change window-title because this function is special, and needs to be called before "
              "'elf_init_show_base'")
    loadPrcFileData('', 'window-title ' + title)


def elf_sync(mode):
    if ELF_SHOW_BASE != None:
        print("ELF: failed to change sync-video because this function is special, and needs to be called before "
              "'elf_init_show_base'")
    loadPrcFileData('', f'vsync {mode}')


def elf_show_fps(fps):
    if ELF_SHOW_BASE != None:
        print("ELF: failed to change show-frame-rate-meter because this function is special, and needs to be called "
              "before "
              "'elf_init_show_base'")
    if ELF_PIPELINE_FLAG:
        print("Can't enable legacy FPS counter in modern mode.")
    loadPrcFileData('', 'show-frame-rate-meter ' + str(fps))


def elf_show_scene_graph_analyzer_meter(analyzer):
    if ELF_SHOW_BASE != None:
        print(
            "ELF: failed to change show-scene-graph-analyzer-meter because this function is special, and needs to be called "
            "before "
            "'elf_init_show_base'")
    loadPrcFileData('', 'show-scene-graph-analyzer-meter ' + str(int(analyzer)))


def elf_fullscreen(mode):
    if ELF_SHOW_BASE != None:
        print("ELF: failed to change fullscreen because this function is special, and needs to be called "
              "before "
              "'elf_init_show_base'")
    loadPrcFileData('', "fullscreen " + str(mode))


def elf_render_resolution(w, h):
    if ELF_SHOW_BASE != None:
        print("ELF: failed to change render-res because this function is special, and needs to be called "
              "before "
              "'elf_init_show_base'")

    loadPrcFileData('', f'win-size {w} {h}')


def elf_camera_fov(fov):
    ELF_SHOW_BASE.camLens.setFov(fov)


def elf_daytime_manager(time):
    if not ELF_PIPELINE_FLAG:
        print("Can't change pipeline daytime, because legacy pipeline is enabled!")
        return
    ELF_PIPELINE.daytime_mgr.time = time


def elf_use_assimp():
    if ELF_SHOW_BASE != None:
        print("ELF: failed to change load-file-type because this function is special, and needs to be called "
              "before "
              "'elf_init_show_base'")
    loadPrcFileData('', 'load-file-type p3assimp')


def elf_parse_glsl(vertex, fragment):
    if ELF_PIPELINE_FLAG:
        print("Can't parse and use raw GLSL shaders, because ELF is using RenderPipeline")
        return -1
    shader = Shader.load(Shader.SL_GLSL, vertex=vertex, fragment=fragment)
    id = elf_gen_id()
    ELF_SHADERS[id] = shader
    return id


def elf_attach_shader_to_model(model_id, shader_id):
    if ELF_PIPELINE_FLAG:
        print("Can't attach raw GLSL shader, because engine using RenderPipeline")
    ELF_OBJECTS[model_id].setShader(ELF_SHADERS[shader_id])
    return model_id


def elf_attach_pipeline_effect(model_id, effect, options=None):
    if not ELF_PIPELINE_FLAG:
        print("Can't attach pipeline effect when it is disabled!")
        return
    if options is None:
        options = {}
    ELF_PIPELINE.set_effect(ELF_OBJECTS[model_id], effect, options)


def elf_set_in_glsl(model_id, uniform_name, value):
    if not ELF_PIPELINE_FLAG:
        print("Can't attach pipeline effect when it is disabled!")
        return
    ELF_OBJECTS[model_id].setShaderInput(uniform_name, value)
    return model_id


def elf_debug_config():
    ConfigVariableManager.getGlobalPtr().listVariables()


def elf_shade_ambient_light(color=(1, 1, 1)):
    light = AmbientLight('ambient')
    light.setColor((color[0], color[1], color[2], 1.0))
    node = ELF_SHOW_BASE.render.attachNewNode(light)
    ELF_SHOW_BASE.render.setLight(node)


def elf_shade_point_light(position=(0, 0, 0), color=(1, 1, 1), shadows=True, shadows_resolution=1024, energy=500,
                          legacy_energy=(0, 0, 1), radius=1000):
    id = elf_gen_id()
    if ELF_PIPELINE_FLAG:
        light = RP_PointLight()
        light.pos = position
        light.color = color
        light.casts_shadows = shadows
        light.shadow_map_resolution = shadows_resolution
        light.energy = energy
        light.radius = radius
        ELF_PIPELINE.add_light(light)
        ELF_OBJECTS[id] = light
    else:
        light = PointLight('light')
        light.attenuation = legacy_energy
        light.color = (color[0], color[1], color[2], 1)
        light.setShadowCaster(shadows, shadows_resolution, shadows_resolution)
        node = ELF_SHOW_BASE.render.attachNewNode(light)
        node.setPos(position)
        ELF_SHOW_BASE.render.setLight(node)
        ELF_OBJECTS[id] = node
    return id


def elf_shade_directional_light(color=(1, 1, 1), hpr=(0, 0, 0), shadows=True, shadows_resolution=1024):
    id = elf_gen_id()
    light = DirectionalLight('light')
    light.setColor((color[0], color[1], color[2], 1))
    light.setShadowCaster(shadows, shadows_resolution, shadows_resolution)
    node = ELF_SHOW_BASE.render.attachNewNode(light)
    node.setHpr(hpr)
    ELF_SHOW_BASE.render.setLight(node)
    ELF_OBJECTS[id] = light
    return id


def elf_gen_id():
    return random.randint(0, 1000000000000000000)


def elf_loader():
    return ELF_SHOW_BASE.loader


def elf_draw(path, position=(0, 0, 0), scale=(1.0, 1.0, 1.0), rotation=(0, 0, 0), set_two_sided=False, color=None,
             use_lit_pipeline=False, wireframe=False, attach=-1, panda3d_fix=False, shader_id=-1, parent=-1):
    id = elf_gen_id()
    ELF_OBJECTS[id] = elf_loader().loadModel(path)
    ELF_OBJECTS[id].setPos(position[0], position[1], position[2])
    ELF_OBJECTS[id].setScale(scale[0], scale[1], scale[2])
    ELF_OBJECTS[id].setHpr(rotation[0], rotation[1], rotation[2])
    ELF_OBJECTS[id].setTwoSided(set_two_sided)
    if use_lit_pipeline:
        if ELF_PIPELINE_FLAG:
            elf_attach_pipeline_effect(id, "shaders/lit_pipeline.yaml")
        else:
            lit_pipeline_shader = elf_parse_glsl("shaders/lit_pipeline_vert.shader", "shaders/lit_pipeline_frag.shader")
            elf_attach_shader_to_model(id, lit_pipeline_shader)
    if color != None:
        if ELF_PIPELINE_FLAG:
            elf_attach_pipeline_effect(id, "shaders/raw_color.yaml")
            elf_set_in_glsl(id, "color", color)
        else:
            ELF_OBJECTS[id].setColor(color[0], color[1], color[2], 1)
    if wireframe:
        ELF_OBJECTS[id].setRenderModeWireframe()
    if panda3d_fix:
        if ELF_PIPELINE_FLAG:
            elf.elf_attach_pipeline_effect(id, "shaders/panda3d-shader.yaml")
    if shader_id != -1:
        elf.elf_attach_shader_to_model(id, shader_id)
    if attach != -1:
        object = ELF_OBJECTS[id]
        del ELF_OBJECTS[id]
        ELF_ATTACHES[attach] = ELF_ATTACHES[attach] + [object] if (attach in ELF_ATTACHES) else [object]
        object.reparentTo(ELF_SHOW_BASE.render)
    elif parent != -1:
        ELF_OBJECTS[id].reparentTo(ELF_OBJECTS[parent])
    else:
        ELF_OBJECTS[id].reparentTo(ELF_SHOW_BASE.render)
    return id


def elf_accept(key, function):
    ELF_SHOW_BASE.accept(key, function)

def elf_clear_space():
    for key in ELF_OBJECTS:
        if type(ELF_OBJECTS[key]) is RP_PointLight:
            ELF_OBJECTS[key].energy = 0
        else:
            ELF_OBJECTS[key].removeNode()

    ELF_OBJECTS.clear()

    if ELF_LAST_SKY != None:
        elf.elf_change_skybox(ELF_LAST_SKY)


def elf_runtime_attach_model(parent, child):
    object = ELF_OBJECTS[child]
    ELF_ATTACHES[parent] = ELF_ATTACHES[parent] + [object] if (parent in ELF_ATTACHES) else [object]


def elf_change_skybox(path):
    global ELF_SKYBOX_ID
    global ELF_LAST_SKY
    ELF_LAST_SKY = path
    if ELF_SKYBOX_ID != -1:
        try:
            ELF_OBJECTS[ELF_SKYBOX_ID].removeNode()
        except:
            pass
    ELF_SKYBOX_ID = elf_draw("models/sky.obj", scale=(1000, 1000, 1000), rotation=(0, 90, 0), set_two_sided=True)
    sky_texture = elf_bind_texture(path)
    elf_attach_texture_to_id(ELF_SKYBOX_ID, sky_texture)
    return ELF_SKYBOX_ID


def elf_rotate_object(id, x, y, z):
    hpr = ELF_OBJECTS[id].getHpr()
    ELF_OBJECTS[id].setHpr(hpr[0] + x, hpr[1] + y, hpr[2] + z)


def elf_legacy_change_color(id, color):
    ELF_OBJECTS[id].setColor(color)


def elf_set_two_sided(obj, sides):
    ELF_OBJECTS[obj].setTwoSided(sides)


def elf_bind_texture(path):
    texture = elf_loader().loadTexture(path)
    id = elf_gen_id()
    ELF_TEXTURES[id] = texture
    return id


def elf_attach_textures_to_id(obj, textures):
    textures_array = [ELF_TEXTURES[id] for id in textures]
    ELF_OBJECTS[obj].setTextures(ELF_OBJECTS[obj], *textures_array)


def elf_bind_textures(*args):
    result = []
    for arg in args:
        result.append(elf_bind_texture(arg))
    return result


def elf_attach_texture_to_id(obj, texture):
    ELF_OBJECTS[obj].setTexture(ELF_TEXTURES[texture])


def elf_prefab_noclip():
    controller = MovementController(ELF_SHOW_BASE)
    controller.setup()


def elf_wireframe(wireframe):
    ELF_SHOW_BASE.render.setRenderModeWireframe(wireframe)


def elf_set_update(function):
    global ELF_UPDATE
    ELF_UPDATE = function
    ELF_SHOW_BASE.taskMgr.add(elf_gen_update_function, "update")


def elf_gen_update_function(task):
    ELF_UPDATE()
    elf_update_attaches()
    return task.cont


def elf_update_attaches():
    print(ELF_ATTACHES)
    for parent_id in ELF_ATTACHES:
        parent = ELF_OBJECTS[parent_id]
        children = ELF_ATTACHES[parent_id]
        for child in children:
            child.setPos(parent.getPos())
            try:
                child.setHpr(parent.getHpr())
            except:
                pass
            try:
                child.setScale(parent.getScale())
            except:
                pass


def elf_get_pos(id):
    return ELF_OBJECTS[id].getPos()


def elf_get_scale(id):
    return ELF_OBJECTS[id].getScale()


def elf_get_hpr(id):
    return ELF_OBJECTS[id].getHpr()


def elf_win_w():
    return ELF_SHOW_BASE.win.getXSize()


def elf_win_h():
    return ELF_SHOW_BASE.win.getYSize()


def elf_add_task(task, task_name):
    ELF_SHOW_BASE.taskMgr.add(task, task_name)


def elf_render_window():
    if ELF_UPDATE == None:
        elf_set_update(lambda: 0)
    if ELF_SHOW_BASE.pipe.getInterfaceName() != 'OpenGL':
        print("This program requires OpenGL.")
        exit(1)
    if ELF_PIPELINE_FLAG:
        ELF_PIPELINE.add_environment_probe()
    ELF_SHOW_BASE.run()


def elf_translate_object(id, x, y, z):
    pos = ELF_OBJECTS[id].getPos()
    ELF_OBJECTS[id].setPos(pos[0] + x, pos[1] + y, pos[2] + z)
