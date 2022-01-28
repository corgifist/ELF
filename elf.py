import random

from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData, ConfigVariableManager, Shader, Material
from direct.filter.CommonFilters import CommonFilters
from rpcore import *
from rpcore.util.movement_controller import MovementController


class ELF_RUNTIME(ShowBase):
    def __init__(self):
        global ELF_PIPELINE
        if not ELF_PIPELINE_FLAG:
            super().__init__()
        else:
            ELF_PIPELINE = RenderPipeline()
            ELF_PIPELINE.set_loading_screen_image("assets/splash.jpg")
            ELF_PIPELINE.create(self)
            ELF_PIPELINE.add_environment_probe()

    def update(self, task):
        pass


ELF_SHOW_BASE: ELF_RUNTIME = None
ELF_OBJECTS = {}
ELF_SHADERS = {}
ELF_TEXTURES = {}
ELF_PIPELINE: RenderPipeline = None
ELF_FILTERS: CommonFilters = None
ELF_PIPELINE_FLAG = True


def elf_enable_mouse():
    ELF_SHOW_BASE.enableMouse()


def elf_switch_to_legacy_pipeline(flag):
    global ELF_PIPELINE_FLAG
    if ELF_SHOW_BASE != None:
        print("Can't switch to legacy pipeline, because ShowBase is ready to use.\nPlease use "
              "'elf_switch_to_legacy_pipeline' before initializing ShowBase!")
    ELF_PIPELINE_FLAG = not flag


def elf_init_show_base():
    global ELF_SHOW_BASE
    elf_win_title('ELF')
    elf_use_assimp()
    ELF_SHOW_BASE = ELF_RUNTIME()
    ELF_SHOW_BASE.disableMouse()


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


def elf_show_fps(fps):
    if ELF_SHOW_BASE != None:
        print("ELF: failed to change show-frame-rate-meter because this function is special, and needs to be called "
              "before "
              "'elf_init_show_base'")
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


def elf_gen_id():
    return random.randint(0, 1000000000000000000)


def elf_loader():
    return ELF_SHOW_BASE.loader


def elf_draw(path, position=(0, 0, 0), scale=(1.0, 1.0, 1.0), rotation=(0, 0, 0), set_two_sided=False):
    id = elf_gen_id()
    ELF_OBJECTS[id] = elf_loader().loadModel(path)
    ELF_OBJECTS[id].setPos(position[0], position[1], position[2])
    ELF_OBJECTS[id].setScale(scale[0], scale[1], scale[2])
    ELF_OBJECTS[id].setHpr(rotation[0], rotation[1], rotation[2])
    ELF_OBJECTS[id].setTwoSided(set_two_sided)
    ELF_OBJECTS[id].reparentTo(ELF_SHOW_BASE.render)
    return id


def elf_set_two_sided(obj, sides):
    ELF_OBJECTS[obj].setTwoSided(sides)


def elf_bind_texture(path):
    texture = elf_loader().loadTexture(path)
    id = elf_gen_id()
    ELF_TEXTURES[id] = texture
    return id


def elf_attach_textures_to_id(obj, textures):
    textures_array = [ELF_TEXTURES[id] for id in ELF_TEXTURES]
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
    ELF_SHOW_BASE.taskMgr.add(function, "update")


def elf_win_w():
    return ELF_SHOW_BASE.win.getXSize()


def elf_win_h():
    return ELF_SHOW_BASE.win.getYSize()


def elf_add_task(task, task_name):
    ELF_SHOW_BASE.taskMgr.add(task, task_name)


def elf_render_window():
    ELF_SHOW_BASE.run()
